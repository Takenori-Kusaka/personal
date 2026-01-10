# Home Assistant プロジェクト - Claude Code 作業メモ

## 現在のバージョン: 6.4 (日本祝日対応版)

## サーバーアクセス情報

| 項目 | 値 |
|------|-----|
| SSH | `ssh kusaka-server@192.168.68.79` |
| サーバーOS | Windows (NUC) |
| Home Assistant | Docker (`homeassistant` コンテナ) |
| 設定パス | `C:/homeassistant/config` (ホスト) → `/config` (コンテナ) |

## デプロイ手順

Windows環境のため、UTF-8ファイル転送にbase64エンコードが必要:

```bash
# 1. ローカルでbase64エンコード
certutil -encode automations.yaml automations_base64.txt

# 2. SCPで転送
scp automations_base64.txt kusaka-server@192.168.68.79:"C:/Users/kusaka-server/automations_base64.txt"

# 3. サーバーでデコード & デプロイ & 再起動
ssh kusaka-server@192.168.68.79 "del C:\\homeassistant\\config\\automations.yaml && certutil -decode C:/Users/kusaka-server/automations_base64.txt C:/homeassistant/config/automations.yaml && del C:\\Users\\kusaka-server\\automations_base64.txt && docker restart homeassistant"

# 4. ローカルの一時ファイル削除
rm automations_base64.txt
```

### Workdayセンサー（UI設定済み）

Workdayインテグレーションは**Home Assistant UIから設定**:
- 設定 → デバイスとサービス → 統合を追加 → Workday
- 国: Japan、勤務日: mon-fri、除外: sat, sun, holiday
- Entity ID: `binary_sensor.workday_sensor`

## 家族構成

| 人物 | 年齢/状況 | GPS追跡 |
|------|----------|---------|
| 父（日下） | 33歳、エンジニア、在宅勤務 | `person.ri_xia` ✅ |
| 母 | 育休中 | 未設定 |
| 娘 | 4歳、保育園 | なし |

**注意**: GPS連動機能は父のみ追跡。他の家族が在宅の可能性があるため、外出検知は書斎のみOFFにしている。

## デバイス構成

### Nature Remo 配置
| 場所 | 機種 | センサー |
|------|------|----------|
| 書斎 | Remo 3 | 温度/湿度/照度/人感 |
| リビング | Remo 3 | 温度/湿度/照度/人感 |
| 子供部屋 | Remo 3 | 温度/湿度/照度/人感 |
| 寝室 | Remo 2 | 温度/湿度のみ |

### スピーカー (Google Home)
| 場所 | Entity ID | 備考 |
|------|-----------|------|
| 書斎 | `media_player.shu_zhai_nohea` | 父専用 + 子供部屋代替 |
| リビング | `media_player.shu_zhai_hetuto_hou_you` | リビング/洗面/玄関エリア |
| 子供部屋 | `media_player.kodomo_heya` | **未導入** (TODO) |

### 照明 (Nature Remo経由)
| 場所 | Entity ID |
|------|-----------|
| 書斎 | `light.shu_zhai` |
| 子供部屋 | `light.zi_gong_bu_wu` |
| リビング | `light.rihinku` |
| 寝室 | `light.qin_shi` |
| 廊下/玄関 | `light.lang_xia` |

### センサー Entity ID
| 種類 | パターン |
|------|----------|
| 温度 | `sensor.temperature_sensor_rihinku`, `_shu_zhai`, `_lang_xia`, `_remo` |
| 湿度 | `sensor.humidity_sensor_*` |
| 照度 | `sensor.illuminance_sensor_*` |
| 人感 | `sensor.movement_sensor_*` (最終検知時刻) |

### エアコン (Nature Remo経由)
| 場所 | Entity ID |
|------|-----------|
| 寝室 | `climate.qin_shi_noeakon_remo` |
| リビング | `climate.rihinkunoeakon_rihinku` |
| 書斎 | `climate.shu_zhai_noeakon_shu_zhai` |
| 子供部屋 | `climate.zi_gong_bu_wu_noeakon_lang_xia` |

**注意**: 21時に全エアコン自動OFF（就寝時節電）

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
| 廊下常夜灯 | `select.signals_lang_xia` | option: "4. night" |
| LG TV | `media_player.lg_webos_tv_ur8000pjb` | ラジオ体操YouTube再生用 |
| TV電源プラグ | `switch.rihinkuterehihuraku` | Tapo P110M（リビングTV） |

## 運用上の制約

| 項目 | 制約内容 |
|------|----------|
| エアコン | 床暖房/床冷房の補助。一部の部屋はリモコン共有で個別制御不可 |
| サーキュレーター | 全部屋一括操作のみ。夜間は睡眠妨害のため使用不可 |
| 人感センサー | 誤検知が多いためユーザーは使用に消極的 |
| 通知 | Companion App通知は未設定。TTS音声通知を使用 |

## TTS音声通知の書き方

```yaml
- service: tts.speak
  target:
    entity_id: tts.google_translate_en_com
  data:
    media_player_entity_id: media_player.shu_zhai_hetuto_hou_you
    message: "メッセージ内容"
    language: ja
```

## Helper Entity (作成済み)

```yaml
# 日本祝日対応センサー（workday.yamlで定義）
binary_sensor:
  - binary_sensor.workday_sensor        # 平日判定（祝日自動除外）

input_boolean:
  - input_boolean.workday              # 平日フラグ（非推奨、workday_japanを使用）
  - input_boolean.father_home          # 父在宅フラグ
  - input_boolean.night_cry_mode       # 夜泣きモード
  # v6.0 新規（動的スケジュール用）- 実際のEntity ID
  - input_boolean.ye_ruteinkai_shi            # 夜ルーティン開始フラグ
  - input_boolean.su_ti_wan_liao              # 宿題完了
  - input_boolean.xi_shi_wan_liao             # 夕食完了
  - input_boolean.ru_yu_wan_liao              # 入浴完了
  - input_boolean.jiu_qin_zhun_bei_wan_liao   # 就寝準備完了

input_datetime:
  - input_datetime.mother_wakeup_time             # 母起床時刻
  - input_datetime.shi_ji_nogui_zhai_shi_guo      # 実際の帰宅時刻（GPS検知で自動記録）
```

## 夜フェーズ固定スケジュール（v6.2）

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

**注**: v6.2で動的スケジュールから固定時刻に変更。テンプレートトリガーの信頼性問題を解消。

## 週次・月次習慣リマインダー

| 頻度 | 内容 | 時刻 |
|------|------|------|
| 毎週土曜 | タオル交換 | 07:00 |
| 毎週土曜 | シーツ洗濯 | 07:00 |
| 毎月1日 | 消耗品交換（歯ブラシ、スポンジ等） | 06:00 |

## ゴミ収集日 (B3地区・梅美台6丁目)

| 種類 | 収集日 | リマインド |
|------|--------|-----------|
| 段ボール | 第4土曜日 | 金曜21:00 |
| 燃えないゴミ/ペットボトル | 第1・3・5木曜日 | 水曜21:00 |
| 粗大ごみ | 個別設定 | 前日21:00 |

## 今後の拡張予定

- [x] 日本の祝日対応 (`binary_sensor.workday_sensor`) ← v6.4で対応済み
- [x] 子供部屋スピーカー導入 (`media_player.zi_gong_bu_wu`) ← 導入済み
- [ ] Phase 2: 夜泣き対応 (2026年2月〜)
- [ ] Companion App通知の有効化
- [ ] Proximity統合（帰宅500m前点灯）
- [ ] 湿度アラート追加
- [ ] 母のGPS追跡追加（全員外出時の全消灯対応）
