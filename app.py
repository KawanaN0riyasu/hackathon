import streamlit as st
from janome.tokenizer import Tokenizer
import re
import plotly.graph_objects as go

# タイトル
st.title("🎤 話し方タイプ診断アプリ")

# 入力
text = st.text_area("📋 日本語原稿を入力してください", height=200)
simulated_audio_duration = st.slider("🕒 仮の録音時間（秒）", 30, 600, 180)

# 形態素解析用
tokenizer = Tokenizer()

# 分析開始
if text:
    # 形態素解析
    tokens = tokenizer.tokenize(text)
    pos_map = {"名詞": [], "動詞": [], "形容詞": []}
    for token in tokens:
        pos = token.part_of_speech.split(',')[0]
        if pos in pos_map:
            pos_map[pos].append(token.surface)

    total_words = sum(len(lst) for lst in pos_map.values())
    noun_count = len(pos_map["名詞"])
    noun_ratio = noun_count / total_words if total_words > 0 else 0

    # 話の速さ（文字／分）
    speed_per_min = len(text) / simulated_audio_duration * 60

    # わかりやすさ（漢字率）
    kanji_count = len(re.findall(r"[一-龥]", text))
    kanji_ratio = kanji_count / len(text) * 100

    # 口癖チェック
    fillers = ["えっと", "えー", "はい"]
    filler_counts = {word: text.count(word) for word in fillers}
    filler_total = sum(filler_counts.values())

    # タイプ診断
    def classify_speed(s): return "🐢 ゆったり" if s < 100 else "🚀 早口気味"
    def classify_info(nr): return "📦 情報詰め派" if nr > 0.4 else "🧘‍♂️ ゆる語り派"
    def classify_clarity(kr): return "🗣️ 平易で親しみやすい" if kr < 30 else "🧠 知的で硬め"
    def classify_fillers(fc): return "🎤 スムーズ" if fc <= 5 else "😅 口癖多め"

    st.subheader("🏅 話し方タイプ診断")
    st.markdown(f"- 話の速さ：{classify_speed(speed_per_min)}")
    st.markdown(f"- 情報量：{classify_info(noun_ratio)}")
    st.markdown(f"- わかりやすさ：{classify_clarity(kanji_ratio)}")
    st.markdown(f"- 口癖指数：{classify_fillers(filler_total)}")

    # 📈 レーダーチャート表示
    # スコアを0〜5スケールに変換
    speed_score = min(speed_per_min / 50, 5)  # 100文字/分 ≒ 2.0
    info_score = min(noun_ratio * 5, 5)       # 最大100% → 5.0
    clarity_score = 5 - min(kanji_ratio / 20, 5)  # 低いほどスコア高
    filler_score = min(filler_total / 2, 5)   # 2回で1点

    labels = ["話の速さ", "情報量", "わかりやすさ", "口癖度"]
    values = [speed_score, info_score, clarity_score, filler_score]
    values += [values[0]]  # 円を閉じる

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels + [labels[0]],
        fill='toself',
        line_color='deepskyblue',
        opacity=0.8
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,5])),
        showlegend=False,
        margin=dict(t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


    st.subheader("📊 詳細スコア")
    st.markdown(f"🕒 話の速さ：**{int(speed_per_min)}文字／分**")
    st.markdown(f"📦 名詞密度：**{noun_count}名詞／{total_words}語**（{round(noun_ratio * 100,1)}%）")
    st.markdown(f"🧩 漢字率：**{kanji_count}漢字／{len(text)}文字**（{round(kanji_ratio,1)}%）")
    st.markdown(f"😅 口癖回数：{'、 '.join([f'{k}：{v}回' for k, v in filler_counts.items()])}（合計：{filler_total}回）")

    st.subheader("💬 フィードバックコメント")
    comments = []
    if speed_per_min > 150:
        comments.append("🚀 少し早口気味かも？聞き手の理解を考慮すると丁寧に話すと◎")
    if noun_ratio > 0.5:
        comments.append("📦 情報がぎっしり！整理されていれば説得力が増します 👍")
    if kanji_ratio > 50:
        comments.append("🧠 専門的な印象あり。やさしい言い換えや例を添えると親切です。")
    if filler_total > 5:
        comments.append("😅 口癖がやや目立ちます。間をとることで印象が整います。")
    if not comments:
        comments.append("🎉 バランスの取れた話し方です！聞き手への配慮が光ってます ✨")

    for c in comments:
        st.markdown(f"- {c}")
