
from openai import OpenAI
import json
import base64
import os


# 画像をbase64にエンコードする関数
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")



def ask_gpt4_turbo(question: str, image_path: str = None):
    api_key = os.getenv('OPENAI_API_KEY')
    # OpenAIのAPIキーを設定
    client = OpenAI(api_key=api_key)

    if image_path is None:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful japanese assistant."},
                {"role": "user", "content": question},
            ]
        )
        print(response)
        return response.choices[0].message.content
    else:
        # 画像をbase64にエンコードする
        base64_image = encode_image(image_path)

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "system", "content": "You are a helpful japanese assistant."},
                {"role": "user", 
                "content": [
                    {"type": "text", "text": question},  # ここに質問を書く
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"},  # 画像の指定の仕方がちょい複雑
                ],},
            ]
        )
        print(response)
        return response.choices[0].message.content

with open('profile.json', 'r', encoding="utf-8") as f:
    data = json.load(f)

# 質問を入力して結果を表示
question = f"""
以下のjsonファイルの内容を元に履歴書に記載の自己PRを800文字程度で作成してください
なお、キャリアとしてテクニカルプロダクトマネージャーを目指しています

```json
{json.dumps(data, separators=(',', ':'))}
```

以下は2023年に作成した自己PRです。ただ、目指すキャリアと限られた文字数の中で不要なものも含まれている可能性がありますので、適宜修正してください。
```txt
私は中学生から寮生活を行い、3年間農業畜産を体験する山村留学をしておりました。その中で自分の
手で作物や家畜をどのように育てるのか、どんな苦労があるのかを経験することが出来ました。
高専入学後は高専ロボコン部に所属し、FW担当として打ち込みました。複数マイコンを用いた9関節
自動制御による人型ロボットのシンクロダンスを目指し、全国大会では特別賞を受賞しました。
太陽精機株式会社、株式会社メイテック、現職と転職を重ねていく中で、装置開発、小型無線機器開発
クラウド開発と幅広く従事し、メカ、エレキ、組み込みソフト、フロントエンド、バックエンド、
インフラシステムと多種多様な経験をしてまいりました。現職でもこの幅広い知見を活かし、これまで
事業部になかった新規知見、新規顧客獲得に繋げる投資案件へ参加し事業部の成長に貢献しました。
組織貢献として社内研修講師によりクラウド人財育成を多く輩出し認定資格合格率90%越えを達成し、
後輩同僚と個人的な1on1などを通じて、同僚間だからこそできる密なコーチングによりプロジェクト
リーダー業務の独立を支援しました。私自身もAWS認定資格五冠を達成するとともに無線技士、電気
工事士の資格などスキル獲得に努め、設備技術勉強会の発表や各展示会への参加を通じて新規技術へ
アンテナを張り続けています。
現職からの転職理由は、さらなるスキル獲得機会とよりよいワークライフバランス獲得を第一に、
より将来性のある職場、経営層の下で自身のスキルを発揮したいためです。
技術成長著しい社会の中で、技術専門性ばかりが先行し、リテラシーのない多くの人がDXなどの
変化に取り残されています。技術はより多くの人を助ける技術であるべきというポリシーのもと
是非とも貴社を通じて社会貢献させてください。

```

また参考として、自己PRの書き方についての指針例の一つ目です
```txt
職務経歴書の自己PR欄は網羅的な内容になるため、履歴書の自己PRでは、応募企業に特化したものや、受賞歴など証明できる事実を記入します。記入欄が限られているので、簡潔にまとめるよう心がけましょう。

履歴書の自己PRにおいて気をつけるべき点を以下で具体的に解説します。

アピールポイントは簡潔にするため1点に絞る
アピールポイントは文章量が多すぎると、伝えたい点が分かりにくくなってしまう可能性があります。そのため、論点を絞って効果的に自分の強みを伝えられる文章を作成しましょう。

・冗長にならないよう強調したい点を簡潔かつ1点に絞る

・結論から書き始める

アピールポイントを裏付けるエピソードを記載する
アピールポイントにはこれまでの仕事の経験や実体験にまつわるエピソードを盛り込みましょう。エピソードは自身の人物像を裏付ける材料になります。面接へと進むためにも、興味を抱いてもらったり共感を得られたりするような内容だとより良いです。

・過去の体験や経験を語るエピソードは、アピールポイントを裏付けるために有効

・エピソードはただ伝えるだけでなく、どう思ってどういう対策をしたのか、結果どうなったのかを理論的な構成にする

```

自己PRの書き方についての指針例の二つ目です

```txt
書き方のポイント・解説
指示されたことを作業としてこなしていただけではなく、自分なりに開発で意識していたことを記載できると良いでしょう。
アップデートなどが定期的に発生すると予見されるシステムの場合は、効率的にプログラムを改修できるように工夫していたことなどもアピールになります。
要件定義や初期段階の設計、顧客との調整業務や折衝なども経験している場合は記載しておきましょう。提案力や調整力が採用担当者に伝わりやすくなり、プラスの評価を得られることもあります。
プロジェクトのリーダーやサブリーダー、後輩育成といったマネジメント経験も強みになるでしょう。
```

"""
# 以下のjsonファイルの内容を元に添付画像の履歴書-2.pngに記載の内容と齟齬があるかチェックしてください。
# 変更点があれば変更箇所を特定し、その内容を記載してください
# 
# ```json
# {json.dumps(data, separators=(',', ':'))}
# ```
# 
# """
# answer = ask_gpt4_turbo(question, "./履歴書-2.png")
answer = ask_gpt4_turbo(question)
print(answer)
