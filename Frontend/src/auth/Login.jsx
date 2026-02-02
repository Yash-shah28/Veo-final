import { useState } from "react";
import api from "../api/client";
import { useAuth } from "./useAuth";

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submit = async () => {
    const res = await api.post("/auth/login", { email, password });
    const token = res.data.access_token;

    // Set token immediately for the next request
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

    const userRes = await api.get("/users/me");
    login(token, userRes.data);
  };

  return (
    <div className="h-screen flex items-center justify-center bg-black text-white">
      <div className="bg-zinc-900 p-6 rounded w-80">
        <input className="w-full mb-3 p-2 text-white bg-zinc-800 border border-zinc-700 rounded" placeholder="Email" onChange={e => setEmail(e.target.value)} />
        <input className="w-full mb-3 p-2 text-white bg-zinc-800 border border-zinc-700 rounded" type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
        <button className="w-full bg-purple-600 hover:bg-purple-700 p-2 rounded transition font-semibold" onClick={submit}>Login</button>
      </div>
    </div>
  );
}
