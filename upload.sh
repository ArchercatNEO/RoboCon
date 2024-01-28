cd "2023-2024";

echo "Packing into zip"
zip -q code.zip $(ls);

echo "Uploading"
curl -X POST http://192.168.4.1/upload/upload -F uploaded_file=@code.zip

rm code.zip

echo "File upload succeeded";
echo "Returning to root";
cd ..;