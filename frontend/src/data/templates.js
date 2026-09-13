export const CODE_TEMPLATES = {
  buffer_overflow: {
    name: "Buffer Overflow (Unbounded Copy)",
    code: `void process_user_input(char *user_data) {\n    char dest_buffer[32];\n    // Unbounded string copy vulnerability\n    strcpy(dest_buffer, user_data);\n    printf("User Data: %s\\n", dest_buffer);\n}`
  },
  null_pointer: {
    name: "Null Pointer Dereference",
    code: `void execute_command(char *cmd_ptr) {\n    // Dereferencing without checking if null\n    if (*cmd_ptr == 'A') {\n        printf("Command A executed\\n");\n    }\n}`
  },
  use_after_free: {
    name: "Use-After-Free Memory Bug",
    code: `void memory_cleanup(char *resource) {\n    free(resource);\n    // Accessing resource after free\n    printf("Resource tag: %c\\n", resource[0]);\n}`
  },
  safe_code: {
    name: "Safe Bounded Copy (Non-Vulnerable)",
    code: `void safe_user_handler(const char *input_str) {\n    char safe_buf[64];\n    // Safe strncpy with boundary check\n    strncpy(safe_buf, input_str, sizeof(safe_buf) - 1);\n    safe_buf[sizeof(safe_buf) - 1] = '\\0';\n}`
  }
};
