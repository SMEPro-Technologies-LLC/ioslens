// iOSLENS Node.js SDK — MCP client (JSON-RPC 2.0)

export interface MCPClientOptions {
  baseUrl?: string;
  token?: string;
  timeout?: number;
}

export interface JSONRPCRequest {
  jsonrpc: '2.0';
  id: number;
  method: string;
  params?: unknown;
}

export interface JSONRPCResponse {
  jsonrpc: '2.0';
  id: number;
  result?: unknown;
  error?: { code: number; message: string; data?: unknown };
}

export class MCPClient {
  private baseUrl: string;
  private token?: string;
  private timeout: number;
  private requestId = 0;

  constructor(options: MCPClientOptions = {}) {
    this.baseUrl = (options.baseUrl ?? 'http://localhost:8001').replace(/\/$/, '');
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

  private nextId(): number {
    return ++this.requestId;
  }

  async rpc(method: string, params?: unknown): Promise<unknown> {
    const req: JSONRPCRequest = {
      jsonrpc: '2.0',
      id: this.nextId(),
      method,
      ...(params !== undefined ? { params } : {}),
    };

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {
      const res = await fetch(`${this.baseUrl}/`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(req),
        signal: controller.signal,
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${await res.text()}`);
      }

      const body = (await res.json()) as JSONRPCResponse;
      if (body.error) {
        throw new Error(`MCP error ${body.error.code}: ${body.error.message}`);
      }
      return body.result;
    } finally {
      clearTimeout(timer);
    }
  }

  async initialize(): Promise<unknown> {
    return this.rpc('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'ioslens-node-sdk', version: '1.0.0' },
    });
  }

  async listTools(): Promise<unknown[]> {
    const result = (await this.rpc('tools/list')) as { tools: unknown[] };
    return result.tools ?? [];
  }

  async callTool(name: string, args: Record<string, unknown>): Promise<unknown> {
    return this.rpc('tools/call', { name, arguments: args });
  }

  async complianceCheck(
    resourceType: string,
    purpose: string,
    userId: string,
    tenantId: string,
    resourceId?: string,
  ): Promise<unknown> {
    return this.callTool('compliance_check', {
      resource_type: resourceType,
      purpose,
      user_id: userId,
      tenant_id: tenantId,
      ...(resourceId ? { resource_id: resourceId } : {}),
    });
  }

  async udmResolve(
    query: string,
    tenantId: string,
    systems?: string[],
  ): Promise<unknown> {
    return this.callTool('udm_resolve', {
      query,
      tenant_id: tenantId,
      ...(systems ? { systems } : {}),
    });
  }
}
