let button = document.querySelector('.btn');
let upload_area = document.querySelector('.drop-area');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    upload_area.addEventListener(eventName, preventDefaults, false)
  })
  function preventDefaults (e) {
    e.preventDefault()
    e.stopPropagation()
  }

upload_area.addEventListener('drop', () =>  console.log('Hello'))
button.addEventListener('click', () => alert('Hello!'));