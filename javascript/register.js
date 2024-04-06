document.addEventListener('DOMContentLoaded', () => {
  const verifySendCodeBtn = document.querySelector('#verifySendCodeBtn');
  const signupBtn = document.querySelector('#signupbtn');

  function isValidUsername(username) {
    return /^[a-zA-Z0-9]+$/.test(username);
  }

  function isValidPassword(password) {
    return /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$/.test(password);
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function sendVerificationCode(email) {
    fetch('/api/send-verification-code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    })
    .then(response => response.json())
    .then(data => {
      if(data.status === 'success') {
        alert('Verification code has been sent to your email.');
        startTimer();
      } else {
        alert(data.message);
      }
    })
    .catch(error => console.error('Error:', error));
  }

  function startTimer() {
    let timeLeft = 90;
    verifySendCodeBtn.disabled = true;
    verifySendCodeBtn.innerText = `Resend code in ${timeLeft} sec.`;

    const timer = setInterval(() => {
      timeLeft -= 1;
      verifySendCodeBtn.innerText = `Resend code in ${timeLeft} sec.`;
      
      if (timeLeft <= 0) {
        clearInterval(timer);
        verifySendCodeBtn.disabled = false;
        verifySendCodeBtn.innerText = 'Send code';
      }
    }, 1000);
  }

  function handleSignUp() {
    const email = document.querySelector('#Email').value.trim();
    const verificationCode = document.querySelector('#verificationCode').value.trim();
    const username = document.querySelector('#username').value.trim();
    const password = document.querySelector('#password').value;
    const repeatPassword = document.querySelector('#Repeatpassword').value;

    if (!isValidEmail(email) || !isValidUsername(username) || !isValidPassword(password) || password !== repeatPassword) {
      alert('Please make sure all fields are correctly filled and passwords match.');
      return;
    }

    fetch('/api/verify-code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code: verificationCode })
    })
    .then(response => response.json())
    .then(data => {
      if(data.status === 'success') {
        registerUser(username, email, password);
      } else {
        alert(data.message);
      }
    })
    .catch(error => console.error('Error:', error));
  }

  function registerUser(username, email, password) {
    fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    })
    .then(response => response.json())
    .then(data => {
      if(data.status === 'success') {
        alert('User successfully registered.');
        // Используйте setTimeout для небольшой задержки перед перенаправлением, обеспечивая закрытие alert.
        setTimeout(function() {
          window.location.href = '/html/index.html'; // Обновите URL в соответствии с вашей структурой проекта
        }, 1000); // Задержка в 1000 мс (1 секунда)
      } else {
        alert(data.message);
      }
    })
    .catch(error => console.error('Error:', error));
  }
  

  verifySendCodeBtn.addEventListener('click', () => sendVerificationCode(document.querySelector('#Email').value.trim()));
  signupBtn.addEventListener('click', handleSignUp);
});
