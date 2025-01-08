import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class AuthService {
  private tokenKey = 'auth_token';
  private _authState = new BehaviorSubject<boolean>(this.hasToken());

  constructor() {
    // Initialize authentication state from localStorage
    const token = this.getToken();
    this._authState.next(!!token);
  }

  // Public getter for the auth state
  get authState() {
    return this._authState.asObservable();
  }

  async login(username: string, password: string): Promise<boolean> {
    try {
      const response = await fetch('https://antwerpen.localhost/api/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: username,
          password: password,
        }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      this.setToken(data.access_token);
      // Update auth state after successful login
      this._authState.next(true);
      return true;
    } catch (error) {
      console.error('Login error:', error);
      this._authState.next(false);
      return false;
    }
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    this._authState.next(false);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  private setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
    this._authState.next(true);
  }

  private hasToken(): boolean {
    return !!this.getToken();
  }

  isAuthenticated(): boolean {
    return this._authState.value;
  }
}