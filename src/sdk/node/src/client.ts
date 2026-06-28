// iOSLENS Node.js SDK — REST client

import type { GovernanceCheckRequest, GovernanceCheckResponse, UDMResolveRequest, UDMResolveResponse } from './index';

export interface IOSLensClientOptions {
  baseUrl?: string;
  token?: string;
  timeout?: number;
}

export class IOSLensClient {
  private baseUrl: string;
  private token?: string;
  private timeout: number;

  constructor(options: IOSLensClientOptions = {}) {
    this.baseUrl = (options.baseUrl ?? 'http://localhost:8000').replace(/\/$/, '');
    this.token = options.token;
    this.timeout = options.timeout ?? 30_000;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (this.token) {
      headers['Authorization'] = `******;
    }
    return headers;
  }

  private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);
    try {
      const res = await fetch(`${this.baseUrl}${path}`, {
        method,
        headers: this.getHeaders(),
        body: body !== undefined ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });
      if (!res.ok) {
        const detail = await res.text();
        throw new Error(`HTTP ${res.status}: ${detail}`);
      }
      return res.json() as Promise<T>;
    } finally {
      clearTimeout(timer);
    }
  }

  async health(): Promise<Record<string, unknown>> {
    return this.request('GET', '/health');
  }

  async governanceCheck(req: GovernanceCheckRequest): Promise<GovernanceCheckResponse> {
    return this.request('POST', '/api/v1/governance/check', req);
  }

  async udmResolve(req: UDMResolveRequest): Promise<UDMResolveResponse> {
    return this.request('POST', '/api/v1/udm/resolve', req);
  }

  async getAuditLogs(params: Record<string, string | number> = {}): Promise<unknown> {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    return this.request('GET', `/api/v1/audit/logs${qs ? '?' + qs : ''}`);
  }

  async verifyAuditChain(): Promise<{ valid: boolean; records_checked: number }> {
    return this.request('GET', '/api/v1/audit/verify');
  }
}
