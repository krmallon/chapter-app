import { HttpClientModule } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { AppRoutingModule } from '../app-routing.module';

import { MessagingService } from './messaging.service';

describe('MessagingService', () => {
  let service: MessagingService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        AppRoutingModule,
        HttpClientModule
      ]
    });
    service = TestBed.inject(MessagingService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
