(function() {
  function buildToolbar(editor) {
    const toolbar = document.createElement('div');
    toolbar.className = 'richtext-toolbar';
    const buttons = [
      { cmd: 'bold', label: 'B' },
      { cmd: 'italic', label: 'I' },
      { cmd: 'underline', label: 'U' },
      { cmd: 'formatBlock', arg: 'p', label: 'P' },
      { cmd: 'formatBlock', arg: 'h3', label: 'H3' },
      { cmd: 'formatBlock', arg: 'blockquote', label: '“”' },
      { cmd: 'fontSize', arg: 2, label: 'S' },
      { cmd: 'fontSize', arg: 3, label: 'M' },
      { cmd: 'fontSize', arg: 4, label: 'L' }
    ];

    buttons.forEach(function(btn) {
      const el = document.createElement('button');
      el.type = 'button';
      el.textContent = btn.label;
      el.addEventListener('click', function(e) {
        e.preventDefault();
        editor.focus();
        document.execCommand(btn.cmd, false, btn.arg || null);
      });
      toolbar.appendChild(el);
    });
    return toolbar;
  }

  function attachRichtext(textarea) {
    const wrapper = document.createElement('div');
    wrapper.className = 'richtext-wrapper';

    const editor = document.createElement('div');
    editor.className = 'richtext-editor';
    editor.contentEditable = 'true';
    editor.innerHTML = textarea.value || '';

    const toolbar = buildToolbar(editor);

    textarea.style.display = 'none';
    textarea.parentNode.insertBefore(wrapper, textarea);
    wrapper.appendChild(toolbar);
    wrapper.appendChild(editor);
    wrapper.appendChild(textarea);

    function sync() {
      textarea.value = editor.innerHTML;
    }

    editor.addEventListener('input', sync);
    if (textarea.form) {
      textarea.form.addEventListener('submit', sync);
    }
  }

  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('textarea.richtext-field').forEach(function(textarea) {
      attachRichtext(textarea);
    });
  });
})();
