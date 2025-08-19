document.addEventListener("DOMContentLoaded", function () {
  const mainMenu = document.getElementById("mainMenu");
  const searchIcon = document.getElementById("searchIcon");
  const loginIcon = document.getElementById("loginIcon");
  const registerIcon = document.getElementById("registerIcon");
  const coursesMenu = document.getElementById("coursesMenu");
  const dropdownMenu = document.getElementById("dropdownMenu");
  const menuToggle = document.getElementById("menuToggle");

  if (registerIcon) {
    registerIcon.addEventListener("click", function () {
      window.location.href = "register.html";
    });
  }

  if (searchIcon) {
    searchIcon.addEventListener("click", function () {
      window.location.href = "search.html";
    });
  }

  if (loginIcon) {
    loginIcon.addEventListener("click", function () {
      window.location.href = "login.html";
    });
  }

  if (coursesMenu && dropdownMenu) {
    coursesMenu.addEventListener("click", function (e) {
      e.preventDefault();
      dropdownMenu.classList.toggle("show");
    });

    document.addEventListener("click", function (e) {
      if (!coursesMenu.contains(e.target) && !dropdownMenu.contains(e.target)) {
        dropdownMenu.classList.remove("show");
      }
    });
  }

  if (menuToggle && mainMenu) {
    menuToggle.addEventListener("click", function () {
      mainMenu.classList.toggle("active");
    });
  }

  const links = document.querySelectorAll("#mainMenu a");
  const currentPath = window.location.pathname.split("/").pop();

  links.forEach((link) => {
    let linkHref = link.getAttribute("href");
    if (linkHref) {
      linkHref = linkHref.split("/").pop();
      if (linkHref === currentPath) {
        link.classList.add("active");
      }
    }
  });
});
