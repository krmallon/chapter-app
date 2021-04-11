import { HttpClientModule } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { AppRoutingModule } from '../app-routing.module';

import { StatService } from './stat.service';

describe('StatService', () => {
  let service: StatService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        AppRoutingModule,
        HttpClientModule
      ]
    });
    service = TestBed.inject(StatService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
