#!/usr/bin/env bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=magazin_moto
DB_USER=postgres
DB_PASS=parola_ta
OUT_FILE=backup_inserts.sql

rm -f "$OUT_FILE"
export PGPASSWORD="$DB_PASS"

tables=(
  shop_brand
  shop_categorie
  shop_produs
  shop_imagineprodus
  shop_variantaprodus
  users_customuser
  orders_comanda
  reviews_review
)

echo "Generez INSERT-uri in $OUT_FILE"
for t in "${tables[@]}"; do
  echo "Tabel: $t"
  pg_dump --column-inserts --data-only --inserts -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$DB_NAME" -t "$t" >> "$OUT_FILE"
done
unset PGPASSWORD
echo "Gata."
