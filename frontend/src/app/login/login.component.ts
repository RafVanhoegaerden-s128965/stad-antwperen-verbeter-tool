import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <div class="login-page">
      <div class="login-container">
        <div class="login-header">
          <h1>Slimme Verbetertool</h1>
          <p>Log in om door te gaan</p>
        </div>
        
        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="login-form">
          <div class="form-group">
            <label for="username">Gebruikersnaam</label>
            <input 
              type="text" 
              id="username" 
              formControlName="username"
              [class.error]="loginForm.get('username')?.touched && loginForm.get('username')?.invalid"
            >
          </div>
          
          <div class="form-group">
            <label for="password">Wachtwoord</label>
            <input 
              type="password" 
              id="password" 
              formControlName="password"
              [class.error]="loginForm.get('password')?.touched && loginForm.get('password')?.invalid"
            >
          </div>

          <button type="submit" [disabled]="loginForm.invalid || isLoading" class="login-button">
            {{ isLoading ? 'Bezig met inloggen...' : 'Inloggen' }}
          </button>

          <div *ngIf="error" class="error-message">
            {{ error }}
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .login-page {
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    .login-container {
      background: white;
      padding: 2.5rem;
      border-radius: 10px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
      width: 100%;
      max-width: 400px;
    }

    .login-header {
      text-align: center;
      margin-bottom: 2rem;
    }

    .login-header h1 {
      color: #2c3e50;
      font-size: 1.8rem;
      margin-bottom: 0.5rem;
    }

    .login-header p {
      color: #7f8c8d;
      font-size: 1rem;
    }

    .login-form {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .form-group label {
      color: #34495e;
      font-size: 0.9rem;
      font-weight: 500;
    }

    .form-group input {
      padding: 0.75rem;
      border: 2px solid #e0e0e0;
      border-radius: 6px;
      font-size: 1rem;
      transition: border-color 0.2s ease;
    }

    .form-group input:focus {
      outline: none;
      border-color: #3498db;
    }

    .form-group input.error {
      border-color: #e74c3c;
    }

    .login-button {
      background-color: #3498db;
      color: white;
      padding: 0.75rem;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.2s ease;
    }

    .login-button:hover:not(:disabled) {
      background-color: #2980b9;
    }

    .login-button:disabled {
      background-color: #bdc3c7;
      cursor: not-allowed;
    }

    .error-message {
      color: #e74c3c;
      text-align: center;
      font-size: 0.9rem;
      padding: 0.5rem;
      background-color: #fdeaea;
      border-radius: 4px;
    }

    @media (max-width: 480px) {
      .login-container {
        padding: 1.5rem;
        margin: 1rem;
      }

      .login-header h1 {
        font-size: 1.5rem;
      }
    }
  `]
})
export class LoginComponent {
  loginForm: FormGroup;
  isLoading = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  async onSubmit() {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.error = '';

      try {
        const success = await this.authService.login(
          this.loginForm.value.username,
          this.loginForm.value.password
        );

        if (success) {
          console.log('Login successful, navigating to home');
          // Give the auth state a moment to update before navigation
          await new Promise(resolve => setTimeout(resolve, 100));
          this.router.navigate(['/home']);
        } else {
          this.error = 'Ongeldige inloggegevens';
        }
      } catch (error) {
        console.error('Login error:', error);
        this.error = 'Inloggen mislukt. Probeer het opnieuw.';
      } finally {
        this.isLoading = false;
      }
    }
  }
}