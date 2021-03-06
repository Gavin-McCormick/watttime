from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from .models import ShiftRequest


class ShiftResource(ModelResource):
    class Meta:
        queryset = ShiftRequest.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        resource_name = 'shift'
        authorization = Authorization()
        ordering = ['date_created']
        filtering = {
            'reqeusted_by': ALL_WITH_RELATIONS,
            'date_created': ALL_WITH_RELATIONS,
            'usage_hours': ALL_WITH_RELATIONS,
            'time_range_hours': ALL_WITH_RELATIONS,
            'recommended_fraction_green': ALL_WITH_RELATIONS,
            'baseline_fraction_green': ALL_WITH_RELATIONS,
            'ba': ['exact'],
        }