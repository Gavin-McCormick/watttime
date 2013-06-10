# set up plot
set output 'isone_marginal_may2013.png' 
set terminal png enhanced size 1280,240
#set title 'ISONE marginal fuels, June 1 2013 (UTC)'
set title 'ISONE marginal fuels, May 2013'
set nokey

# set up x axis
set xdata time
set timefmt "%Y-%m-%d %H:%M:%S-00:00"
#set xrange ["2013-06-01 00:00:00":"2013-06-01 23:59:00"]
set xrange ["2013-05-01 00:00:00":"2013-05-31 23:59:00"]
#set format x "%l %p"

# set up y axis
#set ytics ("Coal" 0, "Oil" 1, "Natural Gas" 2, "Refuse" 3, "Hydro" 4, "Wood" 5, "Nuclear" 6, "Solar" 7, "Wind" 8, "None" 9)
set ytics ("Coal" 0, "Oil" 1, "Natural Gas" 2, "Hydro" 3, "Wood/Biomass" 4)
set yrange [-0.5:4.5]

# set up linestyles w colorbrewer Set1
set style line 1 pt 5 ps 0.7 lc rgb 'black' # coal, black
set style line 2 pt 5 ps 0.7 lc rgb '#666666' # oil, gray
set style line 3 pt 5 ps 0.7 lc rgb '#A65628' # nat gas, brown
set style line 4 pt 5 ps 0.7 lc rgb '#FFFF33' # refuse, yellow
set style line 5 pt 5 ps 0.7 lc rgb '#377EB8' # hydro, blue
set style line 6 pt 5 ps 0.7 lc rgb '#4DAF4A' # wood, green

# plot
plot 'server_responses.tsv' u 1:($3==0 ? 0 : 10) ls 1,\
'' u 1:($3==1 ? 1 : 10) ls 2,\
'' u 1:($3==2 ? 2 : 10) ls 3,\
'' u 1:($3==4 ? 3 : 10) ls 5,\
'' u 1:($3==5 ? 4 : 10) ls 6