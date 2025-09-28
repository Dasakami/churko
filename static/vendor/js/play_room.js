// play_room.js

function initPlayRoom(chatSocket) {
  // Таймеры
  const levelTimerEl = document.getElementById('level-timer');
  const taskTimerEl = document.getElementById('task-timer');

  let levelTime = parseInt(levelTimerEl.dataset.time, 10);
  let taskTime = parseInt(taskTimerEl.dataset.time, 10);

  function updateTimer(el, time) {
    el.querySelector('span').textContent = time;

    if (time > 20) {
      el.className = 'timer green';
    } else if (time > 10) {
      el.className = 'timer yellow';
    } else {
      el.className = 'timer red';
    }
  }

  function tick() {
    if (levelTime > 0) {
      levelTime--;
      updateTimer(levelTimerEl, levelTime);
    }
    if (taskTime > 0) {
      taskTime--;
      updateTimer(taskTimerEl, taskTime);
    }

    if (levelTime <= 0 || taskTime <= 0) {
      clearInterval(interval);
      alert('Время закончилось!');
    }
  }

  updateTimer(levelTimerEl, levelTime);
  updateTimer(taskTimerEl, taskTime);

  const interval = setInterval(tick, 1000);

  // Чат с WebSocket
  const chatBox = document.getElementById('chat-box');
  const chatInput = document.getElementById('chat-message-input');
  const chatBtn = document.getElementById('chat-message-submit');

  chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const messageEl = document.createElement('div');
    messageEl.classList.add('chat-message');
    messageEl.innerHTML = `<strong>${data.username}:</strong> ${data.message}`;
    chatBox.appendChild(messageEl);
    chatBox.scrollTop = chatBox.scrollHeight;
  };

  chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
  };

  chatBtn.onclick = function() {
    const message = chatInput.value.trim();
    if (!message) return;
    chatSocket.send(JSON.stringify({message}));
    chatInput.value = '';
  };

  chatInput.addEventListener('keyup', e => {
    if (e.key === 'Enter') {
      chatBtn.click();
    }
  });
}

window.initPlayRoom = initPlayRoom;
