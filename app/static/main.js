let token = null;

function login() {
  const userId = document.getElementById("user_id").value;
  fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId })
  })
    .then(res => res.json())
    .then(data => {
      token = data.token;
      document.getElementById("output").textContent = "Token recibido: " + token;
    });
}

function getProtected() {
  if (!token) {
    alert("Inicia sesión primero");
    return;
  }
  fetch("/protected", {
    headers: { "Authorization": token }
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("output").textContent = JSON.stringify(data, null, 2);
    });
}

function logout() {
  if (!token) return;
  fetch("/logout", {
    method: "POST",
    headers: { "Authorization": token }
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("output").textContent = data.message;
      token = null;
    });
}
