<template>
  <div>
    <div class="v-intro">
      <div>
        <h1>平台设置</h1>
        <p>平台参数配置与管理。</p>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h3>系统信息</h3></div>
      <div class="card-b">
        <div class="field">
          <label>平台版本</label>
          <input type="text" value="SmartDine V2.0" disabled style="opacity: 0.6" />
        </div>
        <div class="field">
          <label>管理员账号</label>
          <input type="text" value="通过数据库 platform_admin 表管理" disabled style="opacity: 0.6" />
        </div>
        <div class="cap" style="text-align: left; margin-top: 4px">V2.0 基础版本，更多平台参数配置将在后续版本中开放。</div>
      </div>
    </div>
  </div>
</template>
