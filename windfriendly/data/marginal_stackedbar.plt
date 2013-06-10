# set up plot
set output 'isone_marginal_bars_1june2013.png' 
set terminal png enhanced
set title 'Hourly fraction of ISONE marginal fuels, June 1 2013 (UTC)'
set style fill solid #border -1
set boxwidth 1 relative
set key top left

# set up x axis
set xdata time
set timefmt "%H"
set format x "%l %p"

# set up y axis
set yrange [0:1]
set ylabel "fraction of hour on margin"

# set up linestyles w colorbrewer Set1
set style line 1 pt 5 ps 0.7 lc rgb 'black' # coal, black
set style line 2 pt 5 ps 0.7 lc rgb '#666666' # oil, gray
set style line 3 pt 5 ps 0.7 lc rgb '#A65628' # nat gas, brown
set style line 4 pt 5 ps 0.7 lc rgb '#FFFF33' # refuse, yellow
set style line 5 pt 5 ps 0.7 lc rgb '#377EB8' # hydro, blue
set style line 6 pt 5 ps 0.7 lc rgb '#4DAF4A' # wood, green

# plot
plot 'hrfreq_1june2013.csv' u 1:(1) w boxes lc rgb '#EEEEEE' title 'None/no data',\
'' u 1:($2+$4+$5+$6+$7) ls 6 w boxes title 'Wood/Biomass',\
'' u 1:($2+$4+$5+$6) ls 5 w boxes title 'Hydro',\
'' u 1:($2+$4+$5) ls 3 w boxes title 'Natural Gas',\
'' u 1:($2+$3) ls 2 w boxes title 'Oil',\
'' u 1:($2) ls 1 w boxes title 'Coal'

