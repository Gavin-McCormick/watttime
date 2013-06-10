# set up plot
set output 'isone_marginal_hours_1june2013.png' 
set terminal png enhanced
set title 'Frequency of ISONE marginal fuels, June 1 2013 (UTC)'
set style fill solid border -1
set boxwidth 0.9 relative
set nokey

# set up x axis
set xtics ("Coal" 0, "Oil" 1, "Natural Gas" 2, "Hydro" 3, "Wood/Biomass" 4)
set xrange [-0.5:4.5]

# set up y axis
set yrange [0:16]
set ylabel "hours on margin"

# set up linestyles w colorbrewer Set1
set style line 1 pt 5 ps 0.7 lc rgb 'black' # coal, black
set style line 2 pt 5 ps 0.7 lc rgb '#666666' # oil, gray
set style line 3 pt 5 ps 0.7 lc rgb '#A65628' # nat gas, brown
set style line 4 pt 5 ps 0.7 lc rgb '#FFFF33' # refuse, yellow
set style line 5 pt 5 ps 0.7 lc rgb '#377EB8' # hydro, blue
set style line 6 pt 5 ps 0.7 lc rgb '#4DAF4A' # wood, green

# plot
plot 'hist_1june2013.csv' index 0 u 1:2 ls 1 w boxes,\
'' index 1 u 1:2 ls 2 w boxes,\
'' index 2 u 1:2 ls 3 w boxes,\
'' index 3 u 1:2 ls 5 w boxes,\
'' index 4 u 1:2 ls 6 w boxes

#plot 'hist_1june2013.csv' ls 2 w boxes