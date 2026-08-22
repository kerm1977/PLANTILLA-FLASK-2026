document.addEventListener('DOMContentLoaded', function () {
  // Contraseñas
  document.querySelectorAll('.current-password').forEach(function (input) {
    input.addEventListener('input', function () {
      var id = this.id.replace('currentPassword', '');
      var newIn = document.getElementById('newPassword' + id);
      var confIn = document.getElementById('confirmPassword' + id);
      var has = this.value.length > 0;
      newIn.disabled = !has;
      confIn.disabled = !has;
      if (!has) {
        newIn.value = '';
        confIn.value = '';
      }
    });
  });

  var sameModal = document.getElementById('samePasswordModal');
  var sameFlag = document.getElementById('samePasswordFlag');
  if (sameModal && sameFlag && sameFlag.dataset.show === 'true') {
    new bootstrap.Modal(sameModal).show();
  }

  // Edición de nombres
  var editToggle = document.getElementById('editToggle');
  var editIcon = document.getElementById('editIcon');
  var fields = document.querySelectorAll('.profile-value');
  var editing = false;

  if (editToggle && fields.length) {
    fields.forEach(function (el) {
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          editToggle.click();
        }
      });
    });

    editToggle.addEventListener('click', function () {
      if (!editing) {
        fields.forEach(function (el) {
          el.contentEditable = 'true';
          el.classList.add('editing');
        });
        editing = true;
        editIcon.classList.replace('bi-pencil', 'bi-check-lg');
        fields[0].focus();
      } else {
        fields.forEach(function (el) {
          el.contentEditable = 'false';
          el.classList.remove('editing');
          var input = document.getElementById(el.dataset.input);
          if (input) input.value = el.innerText.trim();
        });
        editing = false;
        editIcon.classList.replace('bi-check-lg', 'bi-pencil');
        document.getElementById('profileForm').submit();
      }
    });
  }
});
