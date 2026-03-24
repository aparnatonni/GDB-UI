from flask import Flask, request, jsonify
from pygdbmi.gdbcontroller import GdbController
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

gdb_controller = None
program_name = None

def execute_gdb_command(command):
    response2 = gdb_controller.write(command)
    if response2 is None:
        raise RuntimeError("No response from GDB controller")
    strm = ""
    for rem in response2:
        strm = strm + "\n " + str(rem.get('payload'))
    return strm.strip()

def ensure_exe_extension(name):
    return name if name.endswith('.exe') else name + '.exe'

def start_gdb_session(program):
    global gdb_controller, program_name
    program_name = program
    try:
        gdb_controller = GdbController()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize GDB controller: {e}")

    try:
        response = gdb_controller.write(f"-file-exec-and-symbols {os.path.join('output/', ensure_exe_extension(program_name))}")
        if response is None:
            raise RuntimeError("No response from GDB controller")
    except Exception as e:
        raise RuntimeError(f"Failed to set program file: {e}")
    
    try:
        response = gdb_controller.write("run")
        if response is None:
            raise RuntimeError("No response from GDB controller")
    except Exception as e:
        raise RuntimeError(f"Failed to start program: {e}")

@app.route('/gdb_command', methods=['POST'])
def gdb_command():
    global program_name
    
    # Input validation
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON', 'status': 400}), 400
        
        command = data.get('command', '').strip()
        file = data.get('name', '').strip()
        
        if not command:
            return jsonify({'error': 'Command cannot be empty', 'status': 400}), 400
        if not file:
            return jsonify({'error': 'File name cannot be empty', 'status': 400}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}', 'status': 400}), 400
    
    # GDB execution with proper error handling
    try:
        if program_name != file:
            start_gdb_session(f'{file}')
        
        result = execute_gdb_command(command)
        return jsonify({
            'success': True,
            'result': result,
            'code': f"execute_gdb_command('{command}')"
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 500
        }), 500

@app.route('/compile', methods=['POST'])
def compile_code():
    global program_name
    
    # Input validation
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON', 'status': 400}), 400
        
        code = data.get('code', '').strip()
        name = data.get('name', '').strip()
        
        if not code:
            return jsonify({'error': 'Code cannot be empty', 'status': 400}), 400
        if not name:
            return jsonify({'error': 'File name cannot be empty', 'status': 400}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}', 'status': 400}), 400
    
    # Compile with error handling
    try:
        with open(f'{name}.cpp', 'w') as file:
            file.write(code)

        result = subprocess.run(['g++', f'{name}.cpp', '-o', f'output/{name}.exe'], capture_output=True, text=True)

        if result.returncode == 0:
            program_name = None
            return jsonify({'success': True, 'output': 'Compilation successful.'}), 200
        else:
            return jsonify({'success': False, 'output': result.stderr, 'status': 400}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'status': 500}), 500

@app.route('/upload_file', methods=['POST'])    
def upload_file():
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify({'success': False, 'error': 'No file or name provided'}), 400

    file = request.files['file']
    name = request.form['name']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    file_path = os.path.join('output/', ensure_exe_extension(name))
    file.save(file_path)

    return jsonify({'success': True, 'message': 'File uploaded successfully', 'file_path': file_path})


@app.route('/set_breakpoint', methods=['POST'])
def set_breakpoint():
    global program_name
    
    # Input validation
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON', 'status': 400}), 400
        
        location = data.get('location', '').strip()
        file = data.get('name', '').strip()
        
        if not location:
            return jsonify({'error': 'Breakpoint location cannot be empty', 'status': 400}), 400
        if not file:
            return jsonify({'error': 'File name cannot be empty', 'status': 400}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}', 'status': 400}), 400
    
    # GDB execution with proper error handling
    try:
        if program_name != file:
            start_gdb_session(f'{file}')
        
        result = execute_gdb_command(f"break {location}")
        return jsonify({
            'success': True,
            'result': result,
            'code': f"execute_gdb_command('break {location}')"
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 500
        }), 500

@app.route('/info_breakpoints', methods=['POST'])
def info_breakpoints():
    global program_name
    
    # Input validation
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON', 'status': 400}), 400
        
        file = data.get('name', '').strip()
        
        if not file:
            return jsonify({'error': 'File name cannot be empty', 'status': 400}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}', 'status': 400}), 400
    
    # GDB execution with proper error handling
    try:
        if program_name != file:
            start_gdb_session(f'{file}')
        
        result = execute_gdb_command("info breakpoints")
        return jsonify({
            'success': True,
            'result': result,
            'code': "execute_gdb_command('info breakpoints')"
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 500
        }), 500

@app.route('/stack_trace', methods=['POST'])
def stack_trace():
    global program_name
    
    # Input validation
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON', 'status': 400}), 400
        
        file = data.get('name', '').strip()
        
        if not file:
            return jsonify({'error': 'File name cannot be empty', 'status': 400}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}', 'status': 400}), 400
    
    # GDB execution with proper error handling
    try:
        if program_name != file:
            start_gdb_session(f'{file}')
        
        result = execute_gdb_command("bt")
        return jsonify({
            'success': True,
            'result': result,
            'code': "execute_gdb_command('bt')"
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 500
        }), 500

@app.route('/threads', methods=['POST'])
def threads():
    global program_name
    
    # Input validation
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON', 'status': 400}), 400
        
        file = data.get('name', '').strip()
        
        if not file:
            return jsonify({'error': 'File name cannot be empty', 'status': 400}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}', 'status': 400}), 400
    
    # GDB execution with proper error handling
    try:
        if program_name != file:
            start_gdb_session(f'{file}')
        
        result = execute_gdb_command("info threads")
        return jsonify({
            'success': True,
            'result': result,
            'code': "execute_gdb_command('info threads')"
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 500
        }), 500

@app.route('/get_registers', methods=['POST'])
def get_registers():
    global program_name
    
    # Input validation
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON', 'status': 400}), 400
        
        file = data.get('name', '').strip()
        
        if not file:
            return jsonify({'error': 'File name cannot be empty', 'status': 400}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}', 'status': 400}), 400
    
    # GDB execution with proper error handling
    try:
        if program_name != file:
            start_gdb_session(f'{file}')
        
        result = execute_gdb_command("info registers")
        return jsonify({
            'success': True,
            'result': result,
            'code': "execute_gdb_command('info registers')"
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 500
        }), 500

@app.route('/get_locals', methods=['POST'])
def get_locals():
    global program_name
    
    # Input validation
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON', 'status': 400}), 400
        
        file = data.get('name', '').strip()
        
        if not file:
            return jsonify({'error': 'File name cannot be empty', 'status': 400}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}', 'status': 400}), 400
    
    # GDB execution with proper error handling
    try:
        if program_name != file:
            start_gdb_session(f'{file}')
        
        result = execute_gdb_command("info locals")
        return jsonify({
            'success': True,
            'result': result,
            'code': "execute_gdb_command('info locals')"
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 500
        }), 500

@app.route('/run', methods=['POST'])
def run_program():
    global program_name
    
    # Input validation
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON', 'status': 400}), 400
        
        file = data.get('name', '').strip()
        
        if not file:
            return jsonify({'error': 'File name cannot be empty', 'status': 400}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}', 'status': 400}), 400
    
    # GDB execution with proper error handling
    try:
        if program_name != file:
            start_gdb_session(f'{file}')
        
        result = execute_gdb_command("run")
        return jsonify({
            'success': True,
            'result': result,
            'code': "execute_gdb_command('run')"
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 500
        }), 500

@app.route('/memory_map', methods=['POST'])
def memory_map():
    global program_name
    
    # Input validation
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON', 'status': 400}), 400
        
        file = data.get('name', '').strip()
        
        if not file:
            return jsonify({'error': 'File name cannot be empty', 'status': 400}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}', 'status': 400}), 400
    
    # GDB execution with proper error handling
    try:
        if program_name != file:
            start_gdb_session(f'{file}')
        
        result = execute_gdb_command("info proc mappings")
        return jsonify({
            'success': True,
            'result': result,
            'code': "execute_gdb_command('info proc mappings')"
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 500
        }), 500

@app.route('/continue', methods=['POST'])
def continue_execution():
    global program_name
    data = request.get_json()
    file = data.get('name')
    if program_name != file:
        start_gdb_session(f'{file}')

    try:
        result = execute_gdb_command("continue")
        response = {
            'success': True,
            'result': result,
            'code': "execute_gdb_command('continue')"
        }
    except Exception as e:
        response = {
            'success': False,
            'error': str(e),
            'code': "execute_gdb_command('continue')"
        }
    
    return jsonify(response)

@app.route('/step_over', methods=['POST'])
def step_over():
    global program_name
    data = request.get_json()
    file = data.get('name')
    if program_name != file:
        start_gdb_session(f'{file}')

    try:
        result = execute_gdb_command("next")
        response = {
            'success': True,
            'result': result,
            'code': "execute_gdb_command('next')"
        }
    except Exception as e:
        response = {
            'success': False,
            'error': str(e),
            'code': "execute_gdb_command('next')"
        }
    
    return jsonify(response)

@app.route('/step_into', methods=['POST'])
def step_into():
    global program_name
    data = request.get_json()
    file = data.get('name')
    if program_name != file:
        start_gdb_session(f'{file}')

    try:
        result = execute_gdb_command("step")
        response = {
            'success': True,
            'result': result,
            'code': "execute_gdb_command('step')"
        }
    except Exception as e:
        response = {
            'success': False,
            'error': str(e),
            'code': "execute_gdb_command('step')"
        }
    
    return jsonify(response)

@app.route('/step_out', methods=['POST'])
def step_out():
    global program_name
    data = request.get_json()
    file = data.get('name')
    if program_name != file:
        start_gdb_session(f'{file}')

    try:
        result = execute_gdb_command("finish")
        response = {
            'success': True,
            'result': result,
            'code': "execute_gdb_command('finish')"
        }
    except Exception as e:
        response = {
            'success': False,
            'error': str(e),
            'code': "execute_gdb_command('finish')"
        }
    
    return jsonify(response)

@app.route('/add_watchpoint', methods=['POST'])
def add_watchpoint():
    global program_name
    data = request.get_json()
    variable = data.get('variable')
    file = data.get('name')
    if program_name != file:
        start_gdb_session(f'{file}')

    try:
        result = execute_gdb_command(f"watch {variable}")
        response = {
            'success': True,
            'result': result,
            'code': f"execute_gdb_command('watch {variable}')"
        }
    except Exception as e:
        response = {
            'success': False,
            'error': str(e),
            'code': f"execute_gdb_command('watch {variable}')"
        }
    
    return jsonify(response)

@app.route('/delete_breakpoint', methods=['POST'])
def delete_breakpoint():
    global program_name
    data = request.get_json()
    breakpoint_number = data.get('breakpoint_number')
    file = data.get('name')
    if program_name != file:
        start_gdb_session(f'{file}')

    try:
        result = execute_gdb_command(f"delete {breakpoint_number}")
        response = {
            'success': True,
            'result': result,
            'code': f"execute_gdb_command('delete {breakpoint_number}')"
        }
    except Exception as e:
        response = {
            'success': False,
            'error': str(e),
            'code': f"execute_gdb_command('delete {breakpoint_number}')"
        }
    
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
