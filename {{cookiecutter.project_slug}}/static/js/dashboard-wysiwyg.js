
  // WYSIWYG editor básico
  (function () {
    document.querySelectorAll('[data-cmd]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        const editor = document.getElementById(this.dataset.editor);
        if (!editor) return;
        editor.focus();
        const cmd = this.dataset.cmd;
        const val = this.dataset.val || '';
        document.execCommand(cmd, false, val);
        const target = document.getElementById(editor.dataset.target);
        if (target) target.value = editor.innerHTML;
      });
    });

    document.querySelectorAll('.wysiwyg-editor').forEach(function (ed) {
      ed.addEventListener('input', function () {
        const target = document.getElementById(ed.dataset.target);
        if (target) target.value = ed.innerHTML;
      });
      ed.addEventListener('paste', function (e) {
        e.preventDefault();
        const text = (e.clipboardData || window.clipboardData).getData('text/plain');
        document.execCommand('insertText', false, text);
      });
    });

    document.querySelectorAll('form').forEach(function (form) {
      form.addEventListener('submit', function () {
        form.querySelectorAll('.wysiwyg-editor').forEach(function (ed) {
          const target = document.getElementById(ed.dataset.target);
          if (target) target.value = ed.innerHTML;
        });
      });
    });
  })();
