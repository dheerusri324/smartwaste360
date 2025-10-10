// frontend/src/pages/CollectorLogin.jsx

import React from 'react';
import CollectorLoginForm from '../components/collector/CollectorLoginForm';

const CollectorLogin = () => {
  // This page component renders the form.
  // The AuthLayout is applied by the router in AppRoutes.jsx.
  return (
    <CollectorLoginForm />
  );
};

export default CollectorLogin;