// frontend/src/pages/Register.jsx

import React from 'react';
import RegisterForm from '../components/auth/RegisterForm';

const Register = () => {
  // This page's only job is to render the registration form.
  // The AuthLayout is handled by the router in AppRoutes.jsx.
  return (
    <RegisterForm />
  );
};

export default Register;