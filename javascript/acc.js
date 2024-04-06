document.addEventListener('DOMContentLoaded', function() {
  fetch('/api/user')
    .then(response => {
      if (!response.ok) {
        throw new Error('Не аутентифицирован');
      }
      return response.json();
    })
    .then(data => {
      if (data.status === 'success') {
        document.querySelector("#username").textContent = data.data.username;
        document.querySelector("#email").textContent = data.data.email;
        document.querySelector("#dateRegister").textContent = data.data.dateRegister;
      } else {
        console.error('Ошибка: ' + data.message);
      }
    })
    .catch(error => {
      console.error('Ошибка при получении данных пользователя:', error);
      window.location.href = '/html/login.html';
    });
});

function logout() {
  fetch('/api/logout', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      }
  })
  .then(response => response.json())
  .then(data => {
      if (data.status === 'success') {
          window.location.href = '/html/login.html';
      } else {
          console.error('Ошибка при выходе: ' + data.message);
      }
  })
  .catch(error => console.error('Ошибка при выходе:', error));
}
