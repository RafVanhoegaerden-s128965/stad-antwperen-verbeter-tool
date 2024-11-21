import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent {
  textForm: FormGroup;

  constructor(private fb: FormBuilder) {
    this.textForm = this.fb.group({
      originalText: [''],
      generatedText: [''],
      mediumType: [''],
    });
  }

  onGeneralize() {
    // Implementeer generaliseer logica
    console.log('Generaliseren...');
  }

  onFinalize() {
    // Implementeer finaliseer logica
    console.log('Finaliseren...');
  }
}
