# Home Assistant 自衛隊式スマートホーム規律システム

家族の生活リズムを整えるためのHome Automationsシステム

## 概要

- **対象**: 父(33歳エンジニア)、娘(4歳)、母(育休中)
- **目的**: 時間管理と生活習慣の自動化
- **Version**: 6.2 (夜スケジュール固定時刻版)

## v6.2 変更点

- 夜フェーズを動的スケジュールから固定時刻に変更
- テンプレートトリガーの信頼性問題を解消
- 20:30就寝を基準に逆算したスケジュール
- TV電源はプラグレベル（Tapo P110M）で制御

## デバイス構成

### Nature Remo配置
| 場所 | 機種 | センサー |
|------|------|----------|
| 書斎 | Remo 3 | 温度/湿度/照度/人感 |
| リビング | Remo 3 | 温度/湿度/照度/人感 |
| 子供部屋 | Remo 3 | 温度/湿度/照度/人感 |
| 寝室 | Remo 2 | 温度/湿度 |

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

### センサー (Nature Remo)
| 種類 | Entity ID |
|------|-----------|
| 温度 | `sensor.temperature_sensor_rihinku`, `_shu_zhai`, `_lang_xia`, `_remo` |
| 湿度 | `sensor.humidity_sensor_rihinku`, `_shu_zhai`, `_lang_xia`, `_remo` |
| 照度 | `sensor.illuminance_sensor_rihinku`, `_shu_zhai`, `_lang_xia`, `_remo` |
| 人感 | `sensor.movement_sensor_rihinku`, `_shu_zhai`, `_lang_xia`, `_remo` |

### サーキュレーター（部屋別）
| 場所 | Entity ID |
|------|-----------|
| リビング | `button.send_signal_rihinkunosakiyureta` |
| 書斎 | `button.send_signal_shu_zhai_nosakiyureta` |
| 子供部屋 | `button.send_signal_sakiyureta` |
| 寝室 | `button.send_signal_qin_shi_nosakiyureta` |

### その他デバイス
| デバイス | Entity ID | 備考 |
|----------|-----------|------|
| GPS/Person | `person.ri_xia` | 日下（父） |
| LG TV | `media_player.lg_webos_tv_ur8000pjb` | ラジオ体操YouTube再生用 |
| TV電源プラグ | `switch.rihinkuterehihuraku` | Tapo P110M（リビングTV） |

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
| 06:00 | 娘・起床 + 父・朝食準備 + **サーキュレーターON** |
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

### 夜フェーズ（固定時刻スケジュール）

**20:30ベッドイン、21:00就寝を基準にした固定時刻スケジュール**

| 時刻 | イベント |
|------|----------|
| 18:00 | お迎え準備 + サーキュレーターOFF + TV電源OFF |
| 19:00 | GPS帰宅検知（またはフォールバック）→ おかえりなさい |
| 19:05 | 帰宅後作業（手洗い、着替え、洗濯準備、お風呂掃除・沸かす） |
| 19:15 | 夕食 |
| 19:45 | 食器片付け |
| 19:50 | お風呂 |
| 20:05 | 風呂上がり（保湿・パジャマ） |
| 20:10 | 洗濯物干し・明日の準備 |
| 20:20 | 歯磨き・宿題 + サーキュレーターOFF |
| 20:28 | トイレ・寝る準備 |
| 20:30 | ベッドに入る（リビング消灯・廊下常夜灯・TV電源OFF） |
| 20:45 | 子供部屋消灯 |
| 21:00 | 就寝（実際に寝る時間） |
| 21:55 | 父・就寝5分前 |
| 22:00 | 父・就寝 |

## GPS/プレゼンス連動

| トリガー | アクション |
|----------|-----------|
| 外出5分後 | 書斎のみOFF（他の家族が在宅の可能性があるため） |
| 帰宅（日没後） | リビング・廊下点灯 |

## 温度アラート

| 条件 | アクション |
|------|-----------|
| リビング > 28℃（10分間） | 音声通知「エアコン検討」 |
| 書斎 > 28℃（10分間） | 音声通知「エアコン検討」 |
| リビング < 15℃（10分間） | 音声通知「暖房検討」 |

※ 在宅時・日中のみ（06:00-21:00）

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
  - input_boolean.workday              # 平日フラグ
  - input_boolean.father_home          # 父在宅フラグ
  - input_boolean.night_cry_mode       # 夜泣きモード
  - input_boolean.ye_ruteinkai_shi     # 夜ルーティン開始フラグ（GPSフォールバック用）

input_datetime:
  - input_datetime.mother_wakeup_time             # 母起床時刻
  - input_datetime.shi_ji_nogui_zhai_shi_guo      # 実際の帰宅時刻（GPS検知用）
```

**注意**: v6.2で固定時刻スケジュールに変更したため、タスク完了フラグは不要になりました。

**作成方法**: Home Assistant「設定」→「デバイスとサービス」→「ヘルパー」から作成
詳細は `helpers.yaml` を参照

## 今後の拡張予定

- [ ] 子供部屋スピーカー導入 (`media_player.kodomo_heya`)
- [ ] Phase 2: 夜泣き対応 (2026年2月〜)
- [ ] スマホ通知の有効化（Companion App設定）
- [ ] Proximity統合（帰宅500m前点灯）
- [ ] 湿度アラート追加
