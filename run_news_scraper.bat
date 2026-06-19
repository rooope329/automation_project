:: Run the news scraper

:: プロジェクトディレクトリに移動する
cd /d %~dp0%

:: ddesktop_dockerの起動を待つために10秒待機
timeout /t 10 /nobreak >nul

:: ローカルでchromeを起動する
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --remote-debugging-address=0.0.0.0 --remote-allow-origins=* --user-data-dir="C:\temp\chrome_debug"
timeout /t 10 /nobreak >nul

:: mainブランチの最新のコードをpusllする
git checkout main
git pull origin main

:: docker-compoaseを使用して、ニュース記事のスクレイピングを実施する
docker compose up --build --rm automation python src/for_collect_app.py

:: スクレイピングの実行が終わったら、収集したデータをpushする
git add .
set CURRENT_DATE=%DATE:~0,4%-%DATE:~5,2%-%DATE:~8,2%
git commit -m "ニュースデータ自動収集 %CURRENT_DATE%"
git push origin main

:: chromeを終了する
taskkill /F /IM chrome.exe /FI "CONTAINS C:\temp\chrome_debug"

echo ニュース記事の週次収集が完了しました。



