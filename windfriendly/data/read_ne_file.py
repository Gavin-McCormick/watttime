import json
import csv
import dateutil.parser as dp

ne_fuels = ['Coal', 'Oil', 'Natural Gas', 'Refuse', 'Hydro', 'Wood', 'Nuclear', 'Solar', 'Wind', 'None']

def jsonf_to_tsv(infile, outfile):
    # open csv writer
    outf = csv.writer(open(outfile, 'w'), delimiter='\t')
    
    # open json file
    try:
        jsonf = open(infile, 'r')
    except:
        raise ValueError("can't open input file %s" % infile)

    # loop through lines
    for line in jsonf:
        try:
            linedata = json.loads(line)
        except (TypeError, ValueError):
            continue # expect some json parse errors
        try:
            fuels_data = linedata[0]['data']['GenFuelMixes']['GenFuelMix']        
        except TypeError:
            continue  # expect some json parse errors
        except KeyError:
            print "KeyError:", line
            continue

        # set up storage
        date = None
        gens = [0.0 for x in ne_fuels]
        marginal_fuel = len(ne_fuels)-1
        
        # loop through fuels
        for fuel_elt in fuels_data:
            # get values
            try:
                timestamp = fuel_elt['BeginDate']
                fuel = fuel_elt['FuelCategory']
                gen = fuel_elt['GenMw']
                marginal_flag = fuel_elt['MarginalFlag']
            except KeyError:
                raise ValueError("couldn't parse fuel %s" % fuel_elt)

            # parse values
            if date is None:
                date = dp.parse(timestamp)
            if fuel in ne_fuels:
                fuel_ind = ne_fuels.index(fuel)
                gens[fuel_ind] += gen
                if marginal_flag == 'Y':
                    marginal_fuel = min(marginal_fuel, fuel_ind)
            
        # write to csv
        row = [date, marginal_fuel] + gens
        outf.writerow(row)

if __name__ == '__main__':
    jsonf_to_tsv('server_responses.json', 'server_responses.tsv')

