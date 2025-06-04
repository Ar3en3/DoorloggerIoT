
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyDpBM1ljdG9R1qjtqP3k15YTMTH2yEWEBo",
  authDomain: "doorlogger-auth.firebaseapp.com",
  projectId: "doorlogger-auth",
  storageBucket: "doorlogger-auth.firebasestorage.app",
  messagingSenderId: "556534549702",
  appId: "1:556534549702:web:f8c8629dd6831688119bc7",
  measurementId: "G-SSZ3R519F7"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

async function handleAuth(action) {
  const email = document.getElementById("email").value;
  const pass = document.getElementById("password").value;

  try {
    let userCredential;
    if (action === "login") {
      userCredential = await signInWithEmailAndPassword(auth, email, pass);
    } else {
      userCredential = await createUserWithEmailAndPassword(auth, email, pass);
    }
    const idToken = await userCredential.user.getIdToken();

    await fetch("/sessionLogin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idToken })
    });

    window.location.href = "/dashboard";
  } catch (e) {
    document.getElementById("error-msg").innerText = `Firebase: ${e.code}`;
  }
}

document.getElementById("login-btn").onclick = () => handleAuth("login");
document.getElementById("register-btn").onclick = () => handleAuth("register");

onAuthStateChanged(auth, (user) => {
  if (!user && window.location.pathname.startsWith("/dashboard")) {
    window.location.href = "/login";
  }
});
