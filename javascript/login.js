document.addEventListener('DOMContentLoaded', () => {
  const loginButton = document.querySelector('#signinbtn');
  const modal = document.querySelector('#modal');
  const closeModalButton = modal.querySelector('.close-button');
  const modalText = modal.querySelector('#modal-text');

  const showModal = (message) => {
    modalText.textContent = message;
    modal.style.display = "block";
  }

  closeModalButton.addEventListener('click', () => {
    modal.style.display = "none";
  });

  window.addEventListener('click', (event) => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  loginButton.addEventListener('click', () => {
    const username = document.querySelector('#username').value.trim();
    const password = document.querySelector('#password').value;
    
    if (!username || !password) {
      showModal('Имя пользователя и пароль обязательны');
      return;
    }

    fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        showModal('Вы успешно вошли в систему.');
        setTimeout(() => {
          window.location.href = '/html/index.html';
        }, 2000);
      } else {
        showModal('Неверный пароль или имя пользователя.');
      }
    })
    .catch(error => {
      showModal('Произошла ошибка при попытке входа.');
    });
  });
});
