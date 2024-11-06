import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {MediumSelectComponent} from './components/medium-select/medium-select.component'
import {OutputComponent} from './components/output/output.component'
import {TextInputComponent} from './components/text-input/text-input.component'
import {TextEditorComponent} from './text-editor/text-editor.component'

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet,MediumSelectComponent,OutputComponent,TextInputComponent,TextEditorComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  logoUrl: string = 'https://seeklogo.com/images/S/stad-antwerpen-logo-F659E48C62-seeklogo.com.png';
  outputText: string = '';
  showMessage: boolean = false;  // Voeg deze regel toe

  onTextGenerated(text: string) {
    this.outputText = text;
    this.showMessage = true;  // Zet showMessage op true wanneer tekst gegenereerd is
  }

  onOutputTextChanged(updatedText: string) {
    this.outputText = updatedText;
  }

  onTextFinalized() {
    this.outputText = '';
    this.showMessage = false;  // Zet showMessage op false na finaliseren
  }
}