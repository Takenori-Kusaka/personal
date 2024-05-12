import json

# ファイルからJSONデータを読み込む
with open('profile.json', 'r', encoding='utf-8') as file:
    profile = json.load(file)

# AsciiDoc形式の職務経歴書を作成する
asciidoc = f"""= 職務経歴書: {profile['名前']}
:doctype: article
:sectnums:
:toc: left
:toclevels: 3
:sectlinks:

== 基本情報
* 名前: {profile['名前']}
* 性別: {profile['性別']}
* 生年月日: {profile['生年月日']}
* 年齢: {profile['年齢']}
* 出身地: {profile['出身地']}
* 趣味: {'、'.join(profile['趣味'])}

== 学歴
"""
for key, value in profile['経歴']['学歴'].items():
    asciidoc += f"""* {key}:
** 学校名: {value['学校名']}
** 卒業年月: {value['卒業年月']}
** 備考: {value.get('備考', 'なし')}
"""
    
asciidoc += "\n== 職歴\n"
for exp in profile['経歴']['職歴']:
    asciidoc += f"""* {exp['会社名']} ({exp['期間']['入社年月']} - {exp['期間']['退社年月']})
** 職種: {exp['職種']}
** 業務内容: {exp['業務内容']}
** 退社理由: {exp['退社理由']}
** スキル:"""
    for skill_type, skills in exp['スキル'].items():
        asciidoc += f"\n*** {skill_type}: {', '.join(skills)}"
    for duty in exp['職務']:
        asciidoc += f"""
** 職務経歴:
*** プロジェクト概要: {duty['プロジェクト概要']}
*** 役割: {duty['役割']}
*** 主な担当業務: {', '.join(duty['主な担当業務'])}
*** プロジェクトメンバー数: {duty['プロジェクトメンバー数']}
*** 成果: {', '.join(duty['成果'])}
"""

# 出力ファイル名を指定
output_filename = 'career.adoc'

# AsciiDoc形式のテキストをファイルに書き込む
with open(output_filename, 'w', encoding='utf-8') as file:
    file.write(asciidoc)