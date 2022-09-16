#!/bin/bash

# Update public scripts from working copy and generate PHD thesis attachments folder with up-to-date data.

# Go to root and execute the rest of scripts
unset GIT_DIR

# use negative wildcards https://stackoverflow.com/questions/33924985/why-do-i-get-syntax-error-near-unexpected-token
shopt -s extglob

####################################################################

echo
echo "✅ vyčištění složky \"priloha\""

# remove all files in priloha
rm -rf priloha_py
rm -rf priloha_csv
mkdir priloha_csv
mkdir priloha_py
mkdir priloha_py/scripts


echo
echo "✅ Knihovna skriptů"

cp ../phd/scripts/!(*__pycache__) priloha_py/scripts

# delete unused scripts
rm -rf priloha_py/scripts/csv_file.py
rm -rf priloha_py/scripts/vallex.py

echo
echo "✅ První případová studie"

echo "– data anotace → CSV"
# - další tabulky ?
cp ../phd/chovat_chovávat/_data/all.xlsx priloha_csv/prvni_studie.xlsx
python xlsx_to_csv.py priloha_csv/prvni_studie.xlsx --t="APKS + vztažné,ostatní"
rm priloha_csv/prvni_studie.xlsx

cp ../phd/chovat_chovávat/anotovano.csv priloha_csv/prvni_studie_substantiva.csv.tmp
cut -d ';' -f 1,2,3,4,6 priloha_csv/prvni_studie_substantiva.csv.tmp > priloha_csv/prvni_studie_substantiva.csv # remove helper columns
rm priloha_csv/prvni_studie_substantiva.csv.tmp

# cp ../phd/chovat_chovávat/_data/pos.xlsx priloha_csv/prvni_studie_pos.xlsx # je součástí tištěných příloh.

echo "– data kolokace → CSV"
cp ../phd/chovat_chovávat/_data/collocations.xlsx priloha_csv/prvni_studie_kolokace.xlsx
python xlsx_to_csv.py priloha_csv/prvni_studie_kolokace.xlsx --t="Freq"
rm priloha_csv/prvni_studie_kolokace.xlsx

echo "– skripty"

cp ../phd/01_anotovat.py priloha_py/prvni_studie_anotace_predikativnich_jmen.py
sed -i '/.*# START NOT PUBLIC$/,/.*# END NOT PUBLIC$/d' priloha_py/prvni_studie_anotace_predikativnich_jmen.py # clear not public part

cp ../phd/01_anotovat_po_jednom.py priloha_py/prvni_studie_anotace_dat.py
sed -i '/.*# START NOT PUBLIC$/,/.*# END NOT PUBLIC$/d' priloha_py/prvni_studie_anotace_dat.py # clear not public part

cp ../phd/_data_all_vnp.py priloha_py/prvni_studie_data.py

cp ../phd/_data_statistika.py priloha_py/prvni_studie_anotace_statistika.py

cp ../phd/_data_pos.py priloha_py/prvni_studie_anotace_statistika_pos.py

cp ../phd/_data_kolokace.py priloha_py/prvni_studie_pos_ke_kolokacim.py

echo
echo "✅ Druhá případová studie"

echo "– data → CSV"
cp ../phd/acc/_data/acc_all.xlsx priloha_csv/druha_studie.xlsx
python xlsx_to_csv.py priloha_csv/druha_studie.xlsx --t="data"
rm priloha_csv/druha_studie.xlsx

echo "– skripty"
cp ../phd/anotovat_acc.py priloha_py/druha_studie_anotace_dat.py
cp ../phd/anotovat_acc_merge.py priloha_py/druha_studie_statistika.py


echo
echo "✅ ACC - příručka.ujc.cas.cz"

echo "– Příloha 7 → CSV"
cp ../phd/_langr/acc_kettnerova/prirucka_info.xlsx priloha_csv/priloha_7.xlsx
python xlsx_to_csv.py priloha_csv/priloha_7.xlsx --t="Vše"
rm priloha_csv/priloha_7.xlsx

cp ../phd/homonymie/search_in_prirucka.py priloha_py/homonyma_v_prirucce.py

echo "– statistika"
cp ../phd/homonymie/get_statistics.py priloha_py/homonyma_v_prirucce_statistika.py # todo vyresit

echo
echo "✅ xlsx do csv"
cp xlsx_to_csv.py priloha_py/xlsx_to_csv.py

# echo
# echo "✅ struktura"
cmd //c "tree /a /f ./priloha_py > priloha_py/struktura.txt"
sed -i '1,3d' priloha_py/struktura.txt
sed -i '10d' priloha_py/struktura.txt

# echo
# echo "✅ Commit changes"

# git add style.css
# git add src/*
# git add assets/*
# git commit -m 'Update data & scripts'
