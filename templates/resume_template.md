# 職務経歴書：{{ profile.personal.name }}

**最終更新日**: {{ profile.meta.last_updated }}

---

## 基本情報

- **氏名**: {{ profile.personal.name }}
- **性別**: {{ profile.personal.gender }}
- **生年月日**: {{ profile.personal.birth_date }}
- **年齢**: {{ profile.personal.age }}歳
- **出身地**: {{ profile.personal.location }}
- **趣味**: {{ profile.personal.hobbies | join(', ') }}

---

## 学歴

{% for edu in profile.education %}
### {{ edu.level }}
- **学校名**: {{ edu.school_name }}
{% if edu.department %}- **学科**: {{ edu.department }}{% endif %}
- **卒業年月**: {{ edu.graduation_date }}
{% if edu.notes %}- **備考**: {{ edu.notes }}{% endif %}

{% endfor %}

---

## 職歴

{% for company in profile.career.companies %}
## {{ company.name }}

**在籍期間**: {{ company.period.start_date }} ～ {{ company.period.end_date }}
**職種**: {{ company.position }}

{% if company.business_content %}
**業務内容**: {{ company.business_content }}

{% endif %}
{% if company.reason_for_leaving %}
**退社理由**: {{ company.reason_for_leaving }}

{% endif %}

### 保有スキル

{% if company.skills %}
{% if company.skills.mechanical and company.skills.mechanical|length > 0 %}
**機械設計・メカ**:
{% for skill in company.skills.mechanical %}
- {{ skill }}
{% endfor %}
{% endif %}

{% if company.skills.electrical and company.skills.electrical|length > 0 %}
**電気・エレキ**:
{% for skill in company.skills.electrical %}
- {{ skill }}
{% endfor %}
{% endif %}

{% if company.skills.software and company.skills.software|length > 0 %}
**ソフトウェア**:
{% for skill in company.skills.software %}
- {{ skill }}
{% endfor %}
{% endif %}
{% endif %}

### プロジェクト経験

{% for project in company.projects %}
#### {{ project.title }}

**期間**: {{ project.period.start_date }} ～ {{ project.period.end_date }}
**役割**: {{ project.role }}
**チーム規模**: {{ project.team_size }}

**主な担当業務**:
{% for responsibility in project.responsibilities %}
- {{ responsibility }}
{% endfor %}

**プロジェクト成果**:
{% for achievement in project.achievements %}
- {{ achievement }}
{% endfor %}

{% if project.description %}
**プロジェクト詳細**:
{{ project.description }}
{% endif %}

---

{% endfor %}
{% endfor %}

## 特記事項

本職務経歴書は、YAML形式のデータから自動生成されています。
最新の情報については、GitHub Pages で公開されている Web版をご確認ください。

**生成システム**: {{ profile.meta.generated_by }}
**データバージョン**: {{ profile.meta.version }}