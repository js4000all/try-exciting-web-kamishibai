export function createDomRenderer({
  bg,
  left,
  right,
  name,
  text,
  choices,
}) {
  function setChara(el, on, url) {
    el.style.display = on ? "block" : "none";
    if (url) {
      el.style.background = `center / contain no-repeat url(${url})`;
      el.style.border = "none";
    } else {
      el.style.background = "rgba(255,255,255,0.08)";
      el.style.border = "1px solid rgba(255,255,255,0.15)";
    }
  }

  return {
    setBackground({ bg: bgUrl, bgColor }) {
      if (bgUrl) {
        bg.style.backgroundImage = `url(${bgUrl})`;
        bg.style.backgroundColor = "";
      } else if (bgColor) {
        bg.style.backgroundImage = bgColor;
        bg.style.backgroundColor = "";
      }
    },

    setCharacter(side, { on, url }) {
      setChara(side === "left" ? left : right, on, url);
    },

    setDialogue({ name: dialogueName, text: dialogueText }) {
      name.textContent = dialogueName;
      text.textContent = dialogueText;
    },

    showChoices(choiceArr, onSelect) {
      choices.innerHTML = "";
      for (const choice of choiceArr) {
        const button = document.createElement("button");
        button.className = "choice";
        button.textContent = choice.text;
        button.onclick = (event) => {
          event.stopPropagation();
          onSelect(choice);
        };
        choices.appendChild(button);
      }
    },
  };
}
