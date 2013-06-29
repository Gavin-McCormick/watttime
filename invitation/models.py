import os
import random
import datetime
from django.db import models
from django.conf import settings
from django.utils.http import int_to_base36
from hashlib import sha1
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.timezone import now
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage

#token imports
#from PIL import Image, ImageFont, ImageDraw, ImageOps
from picklefield.fields import PickledObjectField
import urllib2
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from urlparse import urlparse, urlunparse


if getattr(settings, 'INVITATION_USE_ALLAUTH', False):
    import re
    SHA1_RE = re.compile('^[a-f0-9]{40}$')
else:    
    from registration.models import SHA1_RE

site = Site.objects.get_current()
root_url = 'http://%s' % site.domain
    
class InvitationKeyManager(models.Manager):
    def get_key(self, invitation_key):
        """
        Return InvitationKey, or None if it doesn't (or shouldn't) exist.
        """
        try:
            key = self.get(key=invitation_key)
        except self.model.DoesNotExist:
            return None
        
        return key
        
    def is_key_valid(self, invitation_key):
        """
        Check if an ``InvitationKey`` is valid or not, returning a valid key
        or false.
        """
        invitation_key = self.get_key(invitation_key)
        if invitation_key and invitation_key.is_usable():
            return invitation_key
        return False

    def create_invitation(self, user, recipient=('recipient@email.com', 'Sirname', 'Lastname' ), save=True):
        """
        Create an ``InvitationKey`` and returns it.
        
        The key for the ``InvitationKey`` will be a SHA1 hash, generated 
        from a combination of the ``User``'s username and a random salt.
        """
        salt = sha1(str(random.random())).hexdigest()[:5]
        key = sha1("%s%s%s" % (datetime.datetime.now(), salt, user.username)).hexdigest()
        if not save:
            return InvitationKey(from_user=user, key='previewkey00000000', recipient=recipient, date_invited=datetime.datetime.now())
        return self.create(from_user=user, key=key, recipient=recipient)
    
    def create_bulk_invitation(self, user, key, uses, recipient):
        """ Create a set of invitation keys - these can be used by anyone, not just a specific recipient """
        return self.create(from_user=user, key=key, uses_left=uses, recipient=None)

    def remaining_invitations_for_user(self, user):
        """
        Return the number of remaining invitations for a given ``User``.
        """
        invitation_user, created = InvitationUser.objects.get_or_create(
            inviter=user,
            defaults={'invitations_remaining': settings.INVITATIONS_PER_USER})
        return invitation_user.invitations_remaining

    def delete_expired_keys(self):
        for key in self.all():
            if key.key_expired():
                key.delete()


class InvitationKey(models.Model):
    key = models.CharField(_('invitation key'), max_length=40)
    date_invited = models.DateTimeField(_('date invited'), 
                                        auto_now_add=True)
    from_user = models.ForeignKey(User, 
                                  related_name='invitations_sent')
    registrant = models.ManyToManyField(User, null=True, blank=True, 
                                  related_name='invitations_used')
    uses_left = models.IntegerField(default=1)
    
    objects = InvitationKeyManager()
    
    recipient = PickledObjectField(default=None, null=True)
    
    def __unicode__(self):
        return u"Invitation from %s on %s (%s)" % (self.from_user.username, self.date_invited, self.key)
    
    def is_usable(self):
        """
        Return whether this key is still valid for registering a new user.        
        """
        return self.uses_left > 0 and not self.key_expired()
    
    def key_expired(self):
        """
        Determine whether this ``InvitationKey`` has expired, returning 
        a boolean -- ``True`` if the key has expired.
        
        The date the key has been created is incremented by the number of days 
        specified in the setting ``ACCOUNT_INVITATION_DAYS`` (which should be 
        the number of days after invite during which a user is allowed to
        create their account); if the result is less than or equal to the 
        current date, the key has expired and this method returns ``True``.
        
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_INVITATION_DAYS)
        return self.date_invited + expiration_date <= now()
    key_expired.boolean = True
    
    def mark_used(self, registrant):
        """
        Note that this key has been used to register a new user.
        """
        self.uses_left -= 1
        self.registrant.add(registrant)
        default_storage.delete('tokens/%s.png' % self.key)
        self.save()
    
    def get_context(self, sender_note=None):
        invitation_url = root_url + reverse('invitation_invited', kwargs={'invitation_key':self.key})
        exp_date = self.date_invited + datetime.timedelta(days=settings.ACCOUNT_INVITATION_DAYS)
        context = { 'invitation_key': self,
                    'expiration_days': settings.ACCOUNT_INVITATION_DAYS,
                    'from_user': self.from_user,
                    'sender_note': sender_note,
                    'site': site,
                    'root_url': root_url,
                    'expiration_date': exp_date,
                    'recipient': self.recipient,
                   # 'token': self.generate_token(invitation_url),
                    'invitation_url':invitation_url}
        return context
    
    def send_to(self, from_email=settings.DEFAULT_FROM_EMAIL, sender_note=None,):
        """
        Send an invitation email to ``email``.
        """
        context = self.get_context(sender_note)
        
        subject = render_to_string('invitation/invitation_email_subject.txt', context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message_html = render_to_string('invitation/invitation_email.html',context)
        context.update({'sender_note':mark_safe(strip_tags(sender_note))})
        message = render_to_string('invitation/invitation_email.txt',context)
        msg = EmailMultiAlternatives(subject, message, from_email, [self.recipient[0]])
        msg.attach_alternative(message_html, "text/html")
        msg.send()
    
#    def generate_token(self, invitation_url):
#        def stamp(image, text, offset):
#            f = ImageFont.load_default()
#            txt_img=Image.new('RGBA', f.getsize(text))
#            d = ImageDraw.Draw(txt_img)
#            d.text( (0, 0), text,  font=f, fill="#888")
#            exp_img_r = txt_img.rotate(0,  expand=1)
#            iw, ih = image.size
#            tw, th = txt_img.size
#            x = iw/2 - tw/2
#            y = ih/2 - th/2
#            image.paste( exp_img_r, (x,y+offset), exp_img_r)
#            return offset+th
#        
#        #normalize sataic url
#        r_parse = urlparse(root_url, 'http')
#        s_parse = urlparse(settings.STATIC_URL, 'http')
#        s_parts = (s_parse.scheme, s_parse.netloc or r_parse.netloc, s_parse.path, s_parse.params, s_parse.query, s_parse.fragment)
#        static_url = urlunparse(s_parts)
#        
#        #open base token image
#        img_url = static_url+'notification/img/token-invite.png'
#        temp_img = NamedTemporaryFile()    
#        temp_img.write(urllib2.urlopen(img_url).read())
#        temp_img.flush()
#        image = Image.open(temp_img.name)
#
#        #stamp expiration date
#        expiration_date = self.date_invited + datetime.timedelta(days=settings.ACCOUNT_INVITATION_DAYS)
#        exp_text = expiration_date.strftime("%x")
#        stamp(image, exp_text, 18)
#
#        #stamp recipiant name
#        if self.recipient[1]:
#            offset = stamp(image, self.recipient[1], -16)
#        if self.recipient[2]:
#            offset = stamp(image, self.recipient[2], offset)
#        image.save(temp_img.name, "PNG", quality=95)
#        if not default_storage.exists('tokens/%s.png' % self.key):
#            default_storage.save('tokens/%s.png' % self.key, File(temp_img))
#        get_token_url = root_url+reverse('invitation_token', kwargs={'key':self.key})
#        token_html = '<a style="display: inline-block;" href="'+invitation_url+'"><img width="100" height="100" class="token" src="'+get_token_url+'" alt="invitation token"></a>'
#        return token_html
        
class InvitationUser(models.Model):
    inviter = models.ForeignKey(User, unique=True)
    invitations_remaining = models.IntegerField()

    def __unicode__(self):
        return u"InvitationUser for %s" % self.inviter.username

    
def user_post_save(sender, instance, created, **kwargs):
    """Create InvitationUser for user when User is created."""
    if created:
        invitation_user = InvitationUser()
        invitation_user.inviter = instance
        invitation_user.invitations_remaining = settings.INVITATIONS_PER_USER
        invitation_user.save()

models.signals.post_save.connect(user_post_save, sender=User)

def invitation_key_post_save(sender, instance, created, **kwargs):
    """Decrement invitations_remaining when InvitationKey is created."""
    if created:
        invitation_user = InvitationUser.objects.get(inviter=instance.from_user)
        remaining = invitation_user.invitations_remaining
        invitation_user.invitations_remaining = remaining-1
        invitation_user.save()

models.signals.post_save.connect(invitation_key_post_save, sender=InvitationKey)

def invitation_key_pre_delete(sender, instance, **kwargs):
    """Delete token image."""
    try:
        default_storage.delete('tokens/%s.png' % instance.key)
    except:
        pass

models.signals.post_delete.connect(invitation_key_pre_delete, sender=InvitationKey)