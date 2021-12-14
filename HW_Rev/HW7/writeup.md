# giveUflag

快速取得 flag 的做法: x64dbg 在大概 0x401796 的地方下 breakpoint，看是要把下面三個 `call rax` 改成 nop 或是 jump 到 0x4017dd 都可以，然後就可以看到 flag 了

`main` 裡面的 `sub_40184C` 會呼叫兩個函數，第一個函數的回傳結果會傳到第二個函數的參數。

第一個函數 IDA 看起來如下:

```c++
_LIST_ENTRY *sub_401550()
{
  _LIST_ENTRY *v1; // [rsp+40h] [rbp-20h]
  _LIST_ENTRY *i; // [rsp+58h] [rbp-8h]

  v1 = NtCurrentPeb()->Ldr->InMemoryOrderModuleList.Flink;
  for ( i = v1->Flink; i != v1 && wcsicmp((const wchar_t *)i[5].Flink, aK); i = i->Flink )
    ;
  return i[2].Flink;
}
```

就是從 PEB LDR 中 InMemoryOrderModuleList 這個 linked list 中透過比對 `BaseDllName.Buffer` 找 dll 的 address 回傳，那個 `aK` 是 `kernel32.dll` (`C:\Windows\System32\kernel32.dll`)。

第二個函數 IDA 看起來如下:

```c++
void (__fastcall *__fastcall realmain(__int64 kbase))(__int64)
{
  char Buffer[256]; // [rsp+20h] [rbp-60h] BYREF
  _BYTE v3[192]; // [rsp+120h] [rbp+A0h] BYREF
  void (__fastcall *v4)(__int64); // [rsp+1E0h] [rbp+160h]
  void (__fastcall *v5)(__int64); // [rsp+1E8h] [rbp+168h]
  char *String1; // [rsp+1F0h] [rbp+170h]
  __int64 v7; // [rsp+1F8h] [rbp+178h]
  __int64 v8; // [rsp+200h] [rbp+180h]
  int v9; // [rsp+20Ch] [rbp+18Ch]
  __int64 v10; // [rsp+210h] [rbp+190h]
  int *v11; // [rsp+218h] [rbp+198h]
  __int64 addr_pehdr; // [rsp+220h] [rbp+1A0h]
  int j; // [rsp+228h] [rbp+1A8h]
  int i; // [rsp+22Ch] [rbp+1ACh]

  memcpy(v3, &unk_403040, 0xB4ui64);
  memset(Buffer, 0, sizeof(Buffer));
  addr_pehdr = kbase + *(int *)(kbase + 0x3C);
  v11 = (int *)(kbase + *(int *)(addr_pehdr + 0x88));
  v10 = kbase + v11[3];
  v9 = v11[5];
  v8 = kbase + v11[7];
  v7 = kbase + v11[8];
  for ( i = 0; i < v9; ++i )
  {
    String1 = (char *)(kbase + *(int *)(v7 + 4 * i));
    if ( !stricmp(String1, "sleep") )
      break;
  }
  v5 = (void (__fastcall *)(__int64))(kbase + *(int *)(v8 + 4 * i));
  v4 = v5;
  v5(604800000i64);
  puts("https://i.ytimg.com/vi/_T2c8g6Zuq8/maxresdefault.jpg");
  v4(604800000i64);
  puts("https://i.ytimg.com/vi/MY4sFW83yxg/maxresdefault.jpg");
  v4(604800000i64);
  puts("https://i.ytimg.com/vi/OVuZ4vGxVKE/maxresdefault.jpg");
  for ( j = 0; j <= 44; ++j )
    Buffer[j] = off_403020[j] ^ v3[4 * j];
  puts(Buffer);
  return v5;
}
```

這邊可以同時對照 PE-Bear 檢視 `kernel32.dll` 的畫面比較好理解，`kbase + 0x3C` 就是想去讀 PE header 的 offset，然後 `addr_pehdr + 0x88` 就是想取得 `Export Directory` 的位置。

之後就從 export directory 上一個一個找有沒有叫 `sleep` 的函數，`v7` 是 `AddressOfNames`，而 `v8` 是 `AddressOfFunctions`。所以 `v4` 和 `v5` 顯然就是 `sleep` 函數，可以把它 patch 成 nop 或是跳到下面，不然就是把 `off_403020` 和 `unk_403040` 兩個地方的資料拿出來自己 xor 也可以。

Flag: `FLAG{PaRs1N6_PE_aNd_D11_1S_50_C00111!!!!!111}`
