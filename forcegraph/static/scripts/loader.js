 window.onload = function () {
        document.querySelector(".loader-container").style.display = "none";
        document.querySelector("main").style.visibility = "visible";
      };
    setTimeout(function() {
    const element = document.getElementById('error-message');
    if (element) {
      element.style.display = 'none';
    }
  }, 5000);