/**
 * iOSLENS MCP client for Node.js (JSON-RPC 2.0)
 */
export interface MCPRequest {
  jsonrpc: "2.0";
  id: string | number;
  method: string;
  params?: Record<string, unknown>;
}

export interface MCPResponse {
  jsonrpc: "2.0";
  id: string | number;
  result?: unknown;
  error?: { code: number; message: string; data?: unknown };
}

export class MCPClient {
  private baseUrl: string;
  private apiKey: string;
  private requestId = 0;

  constructor(
    baseUrl: string = "http://localhost:8001",
    apiKey: string = ""
  ) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }

  async call(
    method: string,
    params?: Record<string, unknown>
  ): Promise<unknown> {
    const id = ++this.requestId;
    const payload: MCPRequest = {
      jsonrpc: "2.0",
      id,
      method,
      params: params ?? {},
    };

    const res = await fetch(`${this.baseUrl}/mcp`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + this.apiKey,
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data: MCPResponse = await res.json();
    if (data.error) {
      throw new Error(`MCP error ${data.error.code}: ${data.error.message}`);
    }
    return data.result;
  }

  async initialize(): Promise<unknown> {
    return this.call("initialize", { protocolVersion: "2024-11-05" });
  }

  async listTools(): Promise<unknown[]> {
    const result = (await this.call("tools/list")) as {
      tools: unknown[];
    };
    return result.tools;
  }

  async callTool(
    name: string,
    args: Record<string, unknown>
  ): Promise<unknown> {
    return this.call("tools/call", { name, arguments: args });
  }

  async complianceCheck(params: {
    subjectId: string;
    action: string;
    resourceType: string;
    purpose?: string;
  }): Promise<unknown> {
    return this.callTool("compliance_check", {
      subject_id: params.subjectId,
      action: params.action,
      resource_type: params.resourceType,
      purpose: params.purpose ?? "",
    });
  }
}
