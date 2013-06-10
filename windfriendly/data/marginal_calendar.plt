# set up plot
set output 'isone_marginal_calendar.png' 
set terminal png enhanced
set title 'ISONE marginal fuels by day and hour (wrong data)'
set nokey

# set up x axis
set xdata time
set timefmt x "%Y-%m-%d"
set format x "%b %d"
set xlabel 'date'

# set up y axis
#set ydata time
#set timefmt y "%H:%M:%S-04:00"
#set format y "%S"
set yrange [0:24]
set ylabel 'hour of day'

# set up linestyles w colorbrewer Set1
set style line 1 pt 5 ps 1.2 lc rgb 'black' # coal, black
set style line 2 pt 5 ps 1.2 lc rgb '#666666' # oil, gray
set style line 3 pt 5 ps 1.2 lc rgb '#A65628' # nat gas, brown
set style line 4 pt 5 ps 1.2 lc rgb '#FFFF33' # refuse, yellow
set style line 5 pt 5 ps 1.2 lc rgb '#377EB8' # hydro, blue
set style line 6 pt 5 ps 1.2 lc rgb '#4DAF4A' # wood, green

# plot
#plot 'server_responses_unique.tsv' u 1:2
plot 'server_responses_unique.tsv' u 1:($3==0 ? $2 : -1) ls 1 title 'coal',\
'' u 1:($3==1 ? $2 : -1) ls 2 title 'oil',\
'' u 1:($3==2 ? $2 : -1) ls 3 title 'natural gas',\
'' u 1:($3==4 ? $2 : -1) ls 5 title 'hydro',\
'' u 1:($3==5 ? $2 : -1) ls 6 title 'wood/biomass'