import React, { useState } from 'react';
import { authService } from '../services/authService';

const Signup: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.');
      return;
    }

    try {
      const response = await authService.signup({ email, password });
      console.log('회원가입 성공:', response);
      // 회원가입 성공 후 처리 (예: 로그인 페이지로 이동)
    } catch (error) {
      setError('회원가입에 실패했습니다.');
      console.error('회원가입 에러:', error);
    }
  };

  return (
    <div className="signup-container">
      <h2>회원가입</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSignup}>
        <div>
          <label>이메일:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>비밀번호:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div>
          <label>비밀번호 확인:</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">회원가입</button>
      </form>
    </div>
  );
};

export default Signup; 