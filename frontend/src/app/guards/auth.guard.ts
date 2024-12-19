import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return true;

  if (authService.isAuthenticated()) {
    return true;
  }

  router.navigate(['/login']);
  return false;
}; 