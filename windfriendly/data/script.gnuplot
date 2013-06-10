#!/usr/bin/gnuplot
set term png size 900, 700
set size 1.0, 1.0
set xrange [0 : 2016]
set output "data/abs.png"
set title "Energy produced by fuel source"
set xlabel "Time (one sample every 5 minutes for last 7 days)"
set ylabel "Energy produced (MW)"
plot \
    'data/processed' using 1 title 'Refuse' with lines, \
    'data/processed' using 2 title 'Oil' with lines, \
    'data/processed' using 3 title 'Natural Gas' with lines, \
    'data/processed' using 4 title 'Nuclear' with lines, \
    'data/processed' using 5 title 'Landfill Gas' with lines, \
    'data/processed' using 6 title 'Coal' with lines, \
    'data/processed' using 7 title 'Wood' with lines, \
    'data/processed' using 8 title 'Wind' with lines, \
    'data/processed' using 9 title 'Hydro' with lines, \
    'data/processed' using 10 title 'Total' with lines
set ytics 10
set yrange [0 : 100]
set output "data/percent.png"
set title "Percentage of energy from each fuel source"
set xlabel "Time (one sample every 5 minutes for last 7 days)"
set ylabel "Percentage of total energy produced"
plot \
    'data/processed' using ($1*100/$10) title 'Refuse' with lines, \
    'data/processed' using ($2*100/$10) title 'Oil' with lines, \
    'data/processed' using ($3*100/$10) title 'Natural Gas' with lines, \
    'data/processed' using ($4*100/$10) title 'Nuclear' with lines, \
    'data/processed' using ($5*100/$10) title 'Landfill Gas' with lines, \
    'data/processed' using ($6*100/$10) title 'Coal' with lines, \
    'data/processed' using ($7*100/$10) title 'Wood' with lines, \
    'data/processed' using ($8*100/$10) title 'Wind' with lines, \
    'data/processed' using ($9*100/$10) title 'Hydro' with lines
