document.addEventListener('DOMContentLoaded', function() {
  let overlay = document.querySelector('#overlay');
  let contactinfo = document.querySelector('#contactinfo');
  let contactButton = document.querySelector('.support');
  let closeContactWindow = document.querySelector('#closewindow1');
  let guarantinfo = document.querySelector('#guarant');
  let guarantbutton = document.querySelector('.guarantee');

  contactButton.addEventListener('click', function() {
      overlay.style.display = 'block';
      contactinfo.style.display = 'block';
      this.blur();
  });

  guarantbutton.addEventListener('click', function() {
      overlay.style.display = 'block';
      guarantinfo.style.display = 'block';
  });

  closeContactWindow.addEventListener('click', function() {
      overlay.style.display = 'none';
      contactinfo.style.display = 'none';
      guarantinfo.style.display = 'none';
  });

  overlay.addEventListener('click', function() {
      this.style.display = 'none';
      contactinfo.style.display = 'none';
      guarantinfo.style.display = 'none';
  });

  document.addEventListener('keydown', function(event) {
      if (event.key === 'Escape') {
          overlay.style.display = 'none';
          contactinfo.style.display = 'none';
          guarantinfo.style.display = 'none';
      }
  });
});

let profilebutton = document.querySelector('.profile')
profilebutton.addEventListener('click', () => {
  window.location.href = '/html/profile.html';
})

