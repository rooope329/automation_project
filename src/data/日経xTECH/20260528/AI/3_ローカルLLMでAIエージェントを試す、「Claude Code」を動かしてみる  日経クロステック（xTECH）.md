# ローカルLLMでAIエージェントを試す、「Claude Code」を動かしてみる | 日経クロステック（xTECH）

本特集では、手元のパソコンなどで大規模言語モデル（LLM）を動かし、ChatGPTやGeminiのような生成AIのサービスを実現するシステム「ローカルLLM」を取り上げます。パソコンの選定から、プログラミング向けAIエージェントの動かし方までを解説します。本特集は2026年2月～3月時点での情報に基づいています。記事内のパソコン等の価格やソフトウエアのバージョンなどは、2026年2月～3月時点のものです。あらかじめご了承ください。

### Claude CodeをローカルLLMで動かそう

　本特集で述べたように、Ollamaは2026年1月に「ollama launch」コマンドが追加されたことで、他のソフトウエアとの連携がより簡単になりました。ここでは、現時点で代表的なソフトウエア開発向けのAIエージェントである「Claude Code」を、OllamaによるローカルLLMで動かしてみましょう。Windows環境での説明になります。

　初めに下準備です。AIエージェントを動かすためにはできるだけ高性能のLLMが必要です。ここでは、ファイルサイズが51GBと大きいのですが、2026年2月に公開された「Qwen3-Coder-Next」を使います。

　Qwenの公式サイトによると、Qwen3-Coder-Nextは、「コーディングエージェントとローカル開発向け」に設計されたものなので、Claude Codeで使うLLMとしてはピッタリでしょう。MoEのLLMで、総パラメータ数は80B（800億）。推論時はそのうちの3B（30億）個のパラメータを使います。

　コマンドプロンプトを起動し、次のコマンドでQwen3-Coder-Nextをダウンロードしましょう。

[![](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/zuy01.jpg?__scale=w:580,h:103&_sh=0c70420570)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=2013924498)

　次に、Claude Codeをインストールします。次のコマンドを実行します（**図1**）。

[![図1●Claude Codeをインストールする](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/01.jpg?__scale=w:680,h:439&_sh=0230160d30)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=1420927604)

図1●Claude Codeをインストールする

[![](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/zuy02.jpg?__scale=w:580,h:103&_sh=0190c807b0)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=2014848019)

　「Git for Windows」もインストールします。次のURLからインストーラーをダウンロードして、インストールしましょう。

[![](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/zuy03.jpg?__scale=w:580,h:103&_sh=0dc033080d)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=2015771540)

　続いて、作業用のフォルダーを作ります。ここでは「myapp」というフォルダーを作ることにします。myappフォルダーを作ったら、コマンドプロンプトでmyappフォルダーに移動しましょう。これで準備は完了です。

## 2ページ目

#### Claude Codeを起動

　それではollama launchコマンドを使ってClaude Codeを起動します。次のように入力しましょう。

[![](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/zuy04.jpg?__scale=w:680,h:72&_sh=0670470f70)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=2016695061)

　すると、「Download qwen3-coder-next?」と聞かれます。「Yes」を選択するとダウンロード済みであることが確認され、**図**2のClaude Codeの画面が現れます。

[![図2●Claude Codeの画面が現れた](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/02.jpg?__scale=w:680,h:440&_sh=0b60430f08)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=1421851125)

図2●Claude Codeの画面が現れた

　初めに、文字色などのテーマを設定します。ここでは「6. Light mode (ANSI colors only)」を選びます。

　次に、セキュリティに関する注意事項が表示された後、myappフォルダーを信用するかどうかを聞いてくるので、「1. Yes, I trust this folder」を選びます。

#### 立方体が回転するプログラムを作る

　これで**図3**のような画面になり、プロンプトの入力欄が表示されます。早速、次のプロンプトを入力してみます。

[![図3●プロンプトの入力欄が表示される](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/03.jpg?__scale=w:680,h:360&_sh=0730cc0aa0)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=1422774646)

図3●プロンプトの入力欄が表示される

[![](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/zug01.jpg?__scale=w:680,h:229&_sh=0fb0260a60)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=-1076239872)

## 3ページ目

　しばらく待つと、**図4**のようにプログラムが生成され、「rotating\_cube.py」というファイルを作成するかどうかを聞いてくるので、「2. Yes, allow all edits during this session」を選びます。すると、myappフォルダーにrotating\_cube.pyが作られ、**図5**のようにプログラムの説明が表示されました。入力欄には「python rotating\_cube.py」と記述されているので、Enterキーを押すと、見事、立方体のワイヤーフレームが回転するプログラムが動きました（**図6**）。マウスで操作も可能です。

[![図4●プログラムが生成され、ファイルを作成するかどうか聞いてくる](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/04.jpg?__scale=w:680,h:439&_sh=0ca0410f50)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=1423698167)

図4●プログラムが生成され、ファイルを作成するかどうか聞いてくる

[![図5●rotating_cube.pyが作られ、プログラムの説明が表示された](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/05.jpg?__scale=w:680,h:439&_sh=09a0bf0210)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=1424621688)

図5●rotating\_cube.pyが作られ、プログラムの説明が表示された

[![図6●立方体のワイヤーフレームが回転するプログラムが動いた](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/06.jpg?__scale=w:590,h:619&_sh=0e90510550)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=1425545209)

図6●立方体のワイヤーフレームが回転するプログラムが動いた

　ただし、立方体が少し小さいようです。そこで、次のプロンプトを入力します。

[![](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/zug02.jpg?__scale=w:590,h:178&_sh=0220600f20)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=-1075316351)

　しばらく待つと、rotating\_cube.pyを修正するかどうか聞いてくるので、「2. Yes, allow all edits during this session」を選びます。これで**図7**のようにrotating\_cube.pyが修正され、修正されたプログラムが動きました（**図8**）。ちゃんと、立方体が大きく表示されています。

[![図7●rotating_cube.pyが修正された](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/07.jpg?__scale=w:680,h:471&_sh=0cc08b0bf0)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=1426468730)

図7●rotating\_cube.pyが修正された

[![図8●修正されたプログラムが動いた](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/08.jpg?__scale=w:550,h:578&_sh=09d0840690)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=1427392251)

図8●修正されたプログラムが動いた

　以上のように、少し時間はかかりますが、Claude Code＋Ollama＋Qwen3-Coder-NextというローカルLLMのシステムで、プログラムの生成とファイルの作成、プログラムの修正、実行を実現できることがわかりました。

## 4ページ目

軽量で高性能なQwen3.5 9BはローカルLLMの新スタンダードになる！？

第2回ではQwen3.5 35Bを使いました。ただ、Qwen3.5 35BはファイルサイズがQ4\_K\_M形式で22.1GBもあり、大容量のVRAMを搭載するパソコンでないと快適には動きません。ですので、「パラメータ数がもう少し小さいものもあればいいのに…」と思っていたところ、3月2日に「Qwen3.5スモールモデルシリーズ」が公開されました。このシリーズには、**表A**の4モデルがあります。ファイルサイズは1G～6.6GBですから、これなら多くのパソコンで動かせるでしょう。

表A●Qwen3.5スモールモデルシリーズのモデルとパラメータ数

[![表A●Qwen3.5スモールモデルシリーズのモデルとパラメータ数](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/hyoA.jpg?__scale=w:680,h:333&_sh=03706b0ec0)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=-178215434)

　このうちのQwen3.5 9Bは、ファイルサイズ（6.6GB）と性能のバランスが良いLLMのようです。しかも、開発元のAlibaba Cloudが公開したベンチマーク結果によると、Qwen3.5 9Bは、ファイルサイズが13GBのgpt-oss-20bと同等かそれ以上の性能を出しています。さらに、一部のベンチマークでは、ファイルサイズが65GBのgpt-oss-120bよりも良いスコアになっています。2025年8月にgptoss-20b/120bが公開されて以降、gpt-oss-20bは“ローカルLLMのスタンダード”、gpt-oss-120bは“ローカルLLMの最高峰”という位置付けでした。しかし、Qwen3.5、特に軽量なQwen3.5 9Bの登場によってこの状況は変わるかもしれません。Qwen3.5は、gpt-oss-20b/120bがサポートしていないVision（画像解釈）にも対応しています。

　Qwen3.5 9Bは、すでにLM StudioとOllamaで簡単にダウンロードできるので、実際に動かしてみましょう。

　まず、第2回の図13、図14、図15の写真を解釈させてみます。LM StudioでQwen3.5 9Bを読み込んだら、右側のサイドバーを表示し、「システムプロンプト」に「日本語で返答してください。」と記述します。その後、画像ファイルをドラッグ＆ドロップして、入力欄の「↑」ボタンを押します。

　実行結果はいずれも、本特集第2回の図16、図17、図18と同じような適切な内容になりました（**図A**）。

[![図A●Qwen3.5 9Bでの実行例。第2回の図13の画像を解釈させた](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/zuA.jpg?__scale=w:460,h:421&_sh=0fc0d06b0b)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=17414745)

図A●Qwen3.5 9Bでの実行例。第2回の図13の画像を解釈させた

　次に、OllamaでQwen3.5 9Bを読み込み、第3回の記事で入力した「10段の階段があります。～」の問題を記述して、入力欄の「↑」ボタンを押します。こちらも実行結果は、73通りという正しい回答になりました。

　Claude Codeで使えるかどうかも試してみましょう。次のコマンドで起動します。

[![](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/zub01.jpg?__scale=w:680,h:61&_sh=0a20230bb0)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=-1218790981)

　Claude Codeが起動したら、本特集で使った「3次元の立方体のワイヤーフレームが回転する～」のプロンプトを入力してみます。

　しばらく待つと、ファイル「rotate\_cube.py」を生成し、何回か自分でバグを修正した後、プログラムを実行してくれました。ただし、そのプログラムはいくつか不具合があったので、追加で「立方体が回転していません。修正してください。」「立方体の表示が大きすぎます。少し小さくしてください。」「リセットボタンが機能していません。修正してください。」という3つのプロンプトを入力しました（**図B**）。最終的には、**図C**のプログラムが動きました。

[![図B●追加のプロンプトでプログラムを修正](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/zuB.jpg?__scale=w:680,h:439&_sh=0be0c80e40)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=18338266)

図B●追加のプロンプトでプログラムを修正

[![図C●立方体をマウスで回転できるプログラムが動いた](https://cdn-xtech.nikkei.com/atcl/nxt/column/18/03600/042100004/zuC.jpg?__scale=w:490,h:435&_sh=01a0390110)](/atcl/nxt/column/18/03600/042100004/?SS=imgview&FD=19261787)

図C●立方体をマウスで回転できるプログラムが動いた

　Qwen3-Coder-Nextと比べると少し手間はかかったものの、軽量なQwen3.5 9BでもClaude Codeの利用が可能であることを確認しました。本格的に使うのは厳しいかもしれませんが、一度試してみましょう。

### 自分のパソコンで大規模言語モデルを動かす

フォローする

第1回
:   [ローカルLLMを使って得られる、5つのメリットを把握しよう](https://xtech.nikkei.com/atcl/nxt/column/18/03600/042100001/?i_cid=nbpnxt_futurelink_child_01)

第2回
:   [「LM Studio」と「Ollama」を導入、パソコンの性能に応じてパラメータを決定](https://xtech.nikkei.com/atcl/nxt/column/18/03600/042100002/?i_cid=nbpnxt_futurelink_child_02)

第3回
:   [ローカルLLMのサーバー機能を活用し、Pythonプログラムから使う](https://xtech.nikkei.com/atcl/nxt/column/18/03600/042100003/?i_cid=nbpnxt_futurelink_child_03)

閲覧中第4回
:   ローカルLLMでAIエージェントを試す、「Claude Code」を動かしてみる

[![日経ソフトウエア](/images/bpcommon/logo/NSW.png)](https://info.nikkeibp.co.jp/media/NSW/)

**出典：日経ソフトウエア、2026年5月号 pp.6-26 「自分のパソコンで大規模言語モデルを動かそう！」を改題、編集**  
記事は執筆時の情報に基づいており、現在では異なる場合があります。