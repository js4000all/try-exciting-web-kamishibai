export const script = [
  { label: "start" },

  { bgColor: "linear-gradient(135deg, #243B55, #141E30)" },
  { leftOn: true, name: "？？？", text: "……起きてる？" },
  { name: "あなた", text: "……ん、起きてる。" },

  { text: "ここは“最小の紙芝居ノベル”。とりあえず動くやつ。" },

  {
    choice: [
      { text: "話しかける", set: { flag_talk: true }, jump: "talk" },
      { text: "無視する", set: { flag_talk: false }, jump: "ignore" },
    ],
  },

  { label: "talk" },
  { name: "？？？", text: "よし。じゃあ、今日から冒険ね。" },
  { text: "（フラグ flag_talk が立った）" },
  { jumpIf: { key: "flag_talk", equals: true, to: "end" } },

  { label: "ignore" },
  { name: "？？？", text: "えっ、冷た……。" },
  { text: "（フラグ flag_talk は false）" },

  { label: "end" },
  {
    rightOn: true,
    name: "ナレーション",
    text: "ここで終わり。続きはあなたの台本次第！",
  },
];
