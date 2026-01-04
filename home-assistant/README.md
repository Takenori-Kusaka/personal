# Home Assistant 自衛隊式スマートホーム規律システム

家族の生活リズムを整えるためのHome Automationsシステム

## 概要

- **対象**: 父(33歳エンジニア)、娘(4歳)、母(育休中)
- **目的**: 時間管理と生活習慣の自動化
- **Version**: 4.6 (廊下常夜灯対応版)

## デバイス構成

### スピーカー
| 場所 | Entity ID | 用途 |
|------|-----------|------|
| 書斎 | `media_player.shu_zhai_nohea` | 父専用 + 子供部屋代替 |
| リビング | `media_player.shu_zhai_hetuto_hou_you` | リビング/洗面/玄関エリア |
| 子供部屋 | `media_player.kodomo_heya` | 未導入（TODO） |

### 照明 (Nature Remo経由)
| 場所 | Entity ID | 備考 |
|------|-----------|------|
| 書斎 | `light.shu_zhai` | turn_on/turn_off対応 |
| 子供部屋 | `light.zi_gong_bu_wu` | turn_on/turn_off対応 |
| リビング | `light.rihinku` | turn_on/turn_off対応 |
| 寝室 | `light.qin_shi` | turn_on/turn_off対応 |
| 廊下/玄関 | `light.lang_xia` | 常夜灯モード対応 |

### 廊下の常夜灯モード
```yaml
# 常夜灯ON
service: select.select_option
target:
  entity_id: select.signals_lang_xia
data:
  option: "4. night"
```

## 1日のスケジュール

### 朝フェーズ
| 時刻 | イベント |
|------|----------|
| 05:50 | 父・起床 (書斎/リビング/廊下点灯) |
| 06:00 | 娘・起床 + 父・朝食準備 |
| 06:05 | 娘・着替え確認 |
| 06:10 | 娘・洗面指示 |
| 06:20 | 娘・リビング移動 |
| 06:25 | 朝食5分前 |
| 06:30 | 朝食点呼 |
| 06:32 | 朝のかくにんタイム |
| 07:00 | 登園準備開始 |
| 07:10 | 出発5分前 |
| 07:15 | 出発 (一部照明OFF) |
| 07:45 | 在宅勤務開始 |

### 夜フェーズ
| 時刻 | イベント |
|------|----------|
| 18:00 | お迎え準備 |
| 18:50 | 帰宅準備 (リビング/廊下点灯) |
| 19:15 | 帰宅 |
| 19:20 | 帰宅後作業 |
| 19:40 | 夕食5分前 |
| 19:45 | 夕食開始 |
| 20:10 | 入浴5分前 |
| 20:15 | 入浴開始 |
| 20:30 | 歯磨き指示 |
| 20:40 | 巡検5分前 |
| 20:45 | 巡検開始 |
| 20:50 | 布団準備 |
| 20:55 | 娘・就寝5分前 |
| 21:00 | 娘・就寝 (強制消灯) + 父・洗濯物干し |
| 21:55 | 父・就寝5分前 |
| 22:00 | 父・就寝 (廊下は常夜灯モード) |

## リマインダー機能

### ゴミ出し (B3地区・梅美台6丁目)
- **段ボール**: 第4土曜日 → 金曜21:00通知
- **燃えないゴミ/ペットボトル**: 第1・3・5木曜日 → 水曜21:00通知
- **粗大ごみ**: 個別設定

### 定期イベント
- **お弁当の日**: 毎月第3水曜日 → 前日・当日朝通知

### 特別イベント
- automations.yamlに個別追加

## デプロイ方法

1. このファイルを編集
2. Home Assistantサーバーにコピー:
   ```
   C:\homeassistant\config\automations.yaml
   ```
3. Home Assistantで「設定」→「オートメーション」→「オートメーションを再読み込み」

## 必要なHelper Entity

```yaml
input_boolean:
  - input_boolean.workday          # 平日フラグ
  - input_boolean.father_home      # 父在宅フラグ
  - input_boolean.night_cry_mode   # 夜泣きモード

input_datetime:
  - input_datetime.mother_wakeup_time  # 母起床時刻
```

## 今後の拡張予定

- [ ] 子供部屋スピーカー導入 (`media_player.kodomo_heya`)
- [ ] Phase 2: 夜泣き対応 (2026年2月〜)
