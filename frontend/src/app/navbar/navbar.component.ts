import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css',
})

export class NavbarComponent implements OnInit, OnDestroy {
  isAuthorized: boolean = false;
  private authSubscription?: Subscription;
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    // Subscribe to the AuthService's BehaviorSubject
    this.authSubscription = this.authService.authState.subscribe(
      (isAuthenticated: boolean) => {
        console.log('Auth state changed:', isAuthenticated);
        this.isAuthorized = isAuthenticated;
      }
    );

    // Initialize the auth state
    this.isAuthorized = this.authService.isAuthenticated();
  }

  ngOnDestroy() {
    if (this.authSubscription) {
      this.authSubscription.unsubscribe();
    }
  }

  onLogout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}