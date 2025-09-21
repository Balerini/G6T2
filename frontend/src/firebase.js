// src/firebase.js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyAChHBcDvscQRhyM3x6P5a72OOnrAX5zds",
  authDomain: "spm-project-a8896.firebaseapp.com",
  projectId: "spm-project-a8896",
  storageBucket: "spm-project-a8896.firebasestorage.app",
  messagingSenderId: "835438545729",
  appId: "1:835438545729:web:44c3eaa7130c16b6516fc0"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
const db = getFirestore(app);

export { db };
